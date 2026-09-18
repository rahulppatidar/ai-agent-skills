#!/bin/sh
# Plan and install Git Secret Guard prerequisites on macOS/Linux.
# SPDX-License-Identifier: GPL-3.0-only
# Copyright (C) 2026 Rahul Patidar

set -u

GITLEAKS_VERSION="8.30.1"
ACTION="${1:-check}"
WORKFLOW="${2:-pre-push}"
APPROVED_ID=""
if [ "${3:-}" = "--approve" ]; then
    APPROVED_ID="${4:-}"
fi

usage() {
    echo "Usage: setup.sh check|install scan|pre-commit|pre-push [--approve PLAN_ID]" >&2
    exit 2
}

case "$ACTION" in check|install) ;; *) usage ;; esac
case "$WORKFLOW" in scan|pre-commit|pre-push) ;; *) usage ;; esac

OS_RAW=$(uname -s 2>/dev/null) || { echo "Unsupported: cannot identify operating system." >&2; exit 2; }
ARCH_RAW=$(uname -m 2>/dev/null) || { echo "Unsupported: cannot identify CPU architecture." >&2; exit 2; }
case "$OS_RAW" in Linux) PLATFORM="linux" ;; Darwin) PLATFORM="darwin" ;; *) echo "Unsupported platform: $OS_RAW" >&2; exit 2 ;; esac
case "$ARCH_RAW" in x86_64|amd64) ARCH="x64" ;; arm64|aarch64) ARCH="arm64" ;; *) echo "Unsupported architecture: $ARCH_RAW" >&2; exit 2 ;; esac

need_git=false
need_python=false
case "$WORKFLOW" in
    scan) ;;
    pre-commit) need_git=true ;;
    pre-push) need_git=true; need_python=true ;;
esac

install_dir="${XDG_BIN_HOME:-${HOME}/.local/bin}"

git_ok=false
python_ok=false
gitleaks_ok=false
git_path=""
python_path=""
git_version="missing"
python_version="missing"
gitleaks_version="missing"

if command -v git >/dev/null 2>&1; then
    git_ok=true
    git_path=$(command -v git)
    git_version=$(git --version 2>/dev/null || echo "present")
fi
if command -v python3 >/dev/null 2>&1; then
    python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:3])))' 2>/dev/null || echo "unknown")
    if python3 -c 'import sys; raise SystemExit(0 if sys.version_info >= (3, 9) else 1)' >/dev/null 2>&1; then
        python_ok=true
        python_path=$(command -v python3)
    fi
fi
gitleaks_candidate=$(command -v gitleaks 2>/dev/null || true)
if [ -n "$gitleaks_candidate" ]; then
    gitleaks_version=$("$gitleaks_candidate" version 2>/dev/null | tr -d '\r\n' || echo "unknown")
    gitleaks_minor=$(printf '%s' "$gitleaks_version" | sed -n 's/^v*8\.\([0-9][0-9]*\)\..*/\1/p')
    if [ -n "$gitleaks_minor" ] && [ "$gitleaks_minor" -ge 19 ]; then gitleaks_ok=true; fi
fi
if [ "$gitleaks_ok" != true ] && [ -x "$install_dir/gitleaks" ] && [ "$gitleaks_candidate" != "$install_dir/gitleaks" ]; then
    local_gitleaks_version=$("$install_dir/gitleaks" version 2>/dev/null | tr -d '\r\n' || echo "unknown")
    local_gitleaks_minor=$(printf '%s' "$local_gitleaks_version" | sed -n 's/^v*8\.\([0-9][0-9]*\)\..*/\1/p')
    if [ -n "$local_gitleaks_minor" ] && [ "$local_gitleaks_minor" -ge 19 ]; then
        gitleaks_ok=true
        gitleaks_candidate="$install_dir/gitleaks"
        gitleaks_version="$local_gitleaks_version"
    fi
fi

missing=""
append_missing() {
    if [ -n "$missing" ]; then missing="$missing,$1"; else missing="$1"; fi
}
if [ "$need_git" = true ] && [ "$git_ok" != true ]; then append_missing "git"; fi
if [ "$need_python" = true ] && [ "$python_ok" != true ]; then append_missing "python3"; fi
if [ "$gitleaks_ok" != true ]; then append_missing "gitleaks"; fi

package_manager="none"
if [ "$PLATFORM" = "darwin" ] && command -v brew >/dev/null 2>&1; then
    package_manager="brew"
elif [ "$PLATFORM" = "linux" ]; then
    for candidate in apt-get dnf yum zypper pacman apk; do
        if command -v "$candidate" >/dev/null 2>&1; then package_manager="$candidate"; break; fi
    done
fi

archive="gitleaks_${GITLEAKS_VERSION}_${PLATFORM}_${ARCH}.tar.gz"
release_base="https://github.com/gitleaks/gitleaks/releases/download/v${GITLEAKS_VERSION}"

system_packages=""
if [ "$need_git" = true ] && [ "$git_ok" != true ]; then system_packages="git"; fi
if [ "$need_python" = true ] && [ "$python_ok" != true ]; then
    python_package="python3"
    case "$package_manager" in brew|pacman) python_package="python" ;; esac
    if [ -n "$system_packages" ]; then system_packages="$system_packages $python_package"; else system_packages="$python_package"; fi
fi
if [ "$gitleaks_ok" != true ] && [ "$PLATFORM" = "linux" ]; then
    for tool_package in "curl:curl" "tar:tar"; do
        tool=${tool_package%%:*}
        package=${tool_package#*:}
        if ! command -v "$tool" >/dev/null 2>&1; then
            if [ -n "$system_packages" ]; then system_packages="$system_packages $package"; else system_packages="$package"; fi
        fi
    done
    if ! command -v sha256sum >/dev/null 2>&1 && ! command -v shasum >/dev/null 2>&1 && ! command -v openssl >/dev/null 2>&1; then
        if [ -n "$system_packages" ]; then system_packages="$system_packages coreutils"; else system_packages="coreutils"; fi
    fi
fi

package_command="none"
elevate=""
administrator_access="no"
if [ -n "$system_packages" ] && [ "$package_manager" != "brew" ] && [ "$package_manager" != "none" ]; then
    if command -v id >/dev/null 2>&1 && [ "$(id -u)" -eq 0 ]; then
        elevate=""
    elif command -v sudo >/dev/null 2>&1; then
        elevate="sudo"
        administrator_access="likely"
    else
        package_manager="none"
    fi
fi
if [ -n "$system_packages" ]; then
    case "$package_manager" in
        brew) package_command="brew install $system_packages" ;;
        apt-get) package_command="${elevate:+$elevate }apt-get update && ${elevate:+$elevate }apt-get install -y $system_packages" ;;
        dnf) package_command="${elevate:+$elevate }dnf install -y $system_packages" ;;
        yum) package_command="${elevate:+$elevate }yum install -y $system_packages" ;;
        zypper) package_command="${elevate:+$elevate }zypper --non-interactive install $system_packages" ;;
        pacman) package_command="${elevate:+$elevate }pacman -S --needed --noconfirm $system_packages" ;;
        apk) package_command="${elevate:+$elevate }apk add $system_packages" ;;
        none) package_command="unsupported: no recognized package manager or elevation path for $system_packages" ;;
    esac
fi

if [ -n "$system_packages" ]; then
    package_source_plan="$package_manager"
else
    package_source_plan="not-needed"
fi
if [ "$gitleaks_ok" = true ]; then
    gitleaks_plan="gitleaks_action=reuse compatible installation
gitleaks_path=$gitleaks_candidate"
else
    gitleaks_plan="gitleaks_action=install reviewed release
gitleaks_source=$release_base/$archive
gitleaks_checksums=$release_base/gitleaks_${GITLEAKS_VERSION}_checksums.txt
gitleaks_destination=$install_dir/gitleaks
gitleaks_install_method=curl download, published SHA-256 verification, tar extraction, user-local install"
fi

plan="workflow=$WORKFLOW
platform=$PLATFORM/$ARCH
missing=$missing
system_package_source=$package_source_plan
system_package_command=$package_command
$gitleaks_plan
network_required=$([ -n "$missing" ] && echo yes || echo no)
administrator_access=$administrator_access"

if command -v cksum >/dev/null 2>&1; then
    plan_id=$(printf '%s' "$plan" | cksum | awk '{print $1}')
else
    echo "Unsupported: cksum is required to bind approval to the plan." >&2
    exit 2
fi

echo "Git Secret Guard prerequisite check"
echo "workflow: $WORKFLOW"
echo "platform: $PLATFORM/$ARCH"
echo "git: $git_version"
echo "python3: $python_version"
echo "gitleaks: $gitleaks_version"
if [ -z "$missing" ]; then
    echo "status: ready"
    echo "No installation is required."
    echo "gitleaks-path: $gitleaks_candidate"
    if [ "$need_python" = true ]; then echo "python-path: $python_path"; fi
    if [ "$need_git" = true ]; then echo "git-path: $git_path"; fi
    exit 0
fi
echo "status: confirmation-required"
echo "missing: $missing"
echo "plan-id: $plan_id"
echo "plan:"
printf '%s\n' "$plan"

if [ "$ACTION" = "check" ]; then
    exit 10
fi
if [ -z "$APPROVED_ID" ] || [ "$APPROVED_ID" != "$plan_id" ]; then
    echo "Installation refused: rerun only after the user approves this exact plan ID." >&2
    exit 2
fi
if [ -n "$system_packages" ] && [ "$package_manager" = "none" ]; then
    echo "Cannot install required system packages automatically on this platform." >&2
    exit 2
fi

echo "Installing the user-approved prerequisites for plan $plan_id."
if [ -n "$system_packages" ]; then
    case "$package_manager" in
        brew) brew install $system_packages ;;
        apt-get) $elevate apt-get update && $elevate apt-get install -y $system_packages ;;
        dnf) $elevate dnf install -y $system_packages ;;
        yum) $elevate yum install -y $system_packages ;;
        zypper) $elevate zypper --non-interactive install $system_packages ;;
        pacman) $elevate pacman -S --needed --noconfirm $system_packages ;;
        apk) $elevate apk add $system_packages ;;
    esac || { echo "System package installation failed." >&2; exit 2; }
fi

installed_gitleaks=false
if [ "$gitleaks_ok" != true ]; then
    command -v curl >/dev/null 2>&1 || { echo "curl is required to download the reviewed release." >&2; exit 2; }
    if ! command -v sha256sum >/dev/null 2>&1 && ! command -v shasum >/dev/null 2>&1 && ! command -v openssl >/dev/null 2>&1; then
        echo "A SHA-256 tool is required to verify the download." >&2
        exit 2
    fi
    temp_dir=$(mktemp -d "${TMPDIR:-/tmp}/git-secret-guard.XXXXXX") || exit 2
    trap 'rm -rf "$temp_dir"' EXIT HUP INT TERM
    curl --fail --silent --show-error --location "$release_base/$archive" --output "$temp_dir/$archive" || exit 2
    curl --fail --silent --show-error --location "$release_base/gitleaks_${GITLEAKS_VERSION}_checksums.txt" --output "$temp_dir/checksums.txt" || exit 2
    expected=$(awk -v name="$archive" '$2 == name {print $1}' "$temp_dir/checksums.txt")
    [ -n "$expected" ] || { echo "Release checksum entry is missing." >&2; exit 2; }
    if command -v sha256sum >/dev/null 2>&1; then
        actual=$(sha256sum "$temp_dir/$archive" | awk '{print $1}')
    elif command -v shasum >/dev/null 2>&1; then
        actual=$(shasum -a 256 "$temp_dir/$archive" | awk '{print $1}')
    else
        actual=$(openssl dgst -sha256 "$temp_dir/$archive" | awk '{print $NF}')
    fi
    [ "$actual" = "$expected" ] || { echo "Gitleaks checksum verification failed." >&2; exit 2; }
    tar -xzf "$temp_dir/$archive" -C "$temp_dir" gitleaks || exit 2
    mkdir -p "$install_dir" || exit 2
    install -m 0755 "$temp_dir/gitleaks" "$install_dir/gitleaks" || exit 2
    installed_gitleaks=true
fi

if [ "$need_git" = true ]; then git --version >/dev/null 2>&1 || { echo "Git verification failed." >&2; exit 2; }; fi
if [ "$need_python" = true ]; then
    python3 -c 'import sys; raise SystemExit(0 if sys.version_info >= (3, 9) else 1)' || { echo "Python 3.9+ verification failed." >&2; exit 2; }
fi
if [ "$installed_gitleaks" = true ]; then
    gitleaks_path="$install_dir/gitleaks"
else
    gitleaks_path="$gitleaks_candidate"
fi
[ -n "$gitleaks_path" ] || { echo "Gitleaks verification failed." >&2; exit 2; }
"$gitleaks_path" version >/dev/null 2>&1 || { echo "Gitleaks verification failed." >&2; exit 2; }
echo "status: installed-and-verified"
echo "gitleaks-path: $gitleaks_path"
if [ "$need_python" = true ]; then echo "python-path: $(command -v python3)"; fi
if [ "$need_git" = true ]; then echo "git-path: $(command -v git)"; fi
echo "Use this absolute path in hooks if the install directory is not on PATH."
