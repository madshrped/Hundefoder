{
  pkgs ? import <nixpkgs> {
    config = {
      allowUnfree = true;
      android_sdk.accept_license = true;
    };
  },
}:

let
  androidComp = pkgs.androidenv.composeAndroidPackages {
    includeSources = true;
    platformVersions = [ "33" ]; # Android API
    ndkVersion = "25.2.9519653"; # NDK version
    includeNDK = true;
    includeCmake = true;
    abiVersions = [ "arm64-v8a" ];
    cmdLineToolsVersion = "8.0";
    toolsVersion = null;
  };
in

pkgs.mkShell {
  name = "kivy-android-shell";

  buildInputs = with pkgs; [
    git
    lbzip2
    ccache
    libffi
    libltc
    libtool
    libssh
    patch

    openssl
    autoconf
    autoconf-archive
    automake
    libtool
    gettext
    m4
    pkg-config
    clang
    gcc
    glibc
    zip
    unzip
    SDL2
    SDL2_image
    SDL2_ttf
    SDL2_mixer
    freetype
    openjdk17
    python311
    androidComp.androidsdk
  ];

  shellHook = ''
    # --- Java ---
    export JAVA_HOME=${pkgs.openjdk17}
    export PATH=$JAVA_HOME/bin:$PATH

    # --- real SDK and NDK paths ---
    REAL_SDK=${androidComp.androidsdk}/libexec/android-sdk
    REAL_NDK=$REAL_SDK/ndk/25.2.9519653

    # --- fake cmdline-tools overlay for p4a ---
    FAKE_SDK="$PWD/.android-sdk-overlay"
    mkdir -p "$FAKE_SDK/cmdline-tools"

    # --- environment variables for p4a ---
    export PATH=$HOME/.local/share/python-for-android/venv/bin:$PATH
    export ANDROIDSDK="$FAKE_SDK"
    export ANDROIDNDK="$REAL_NDK"
    export ANDROID_SDK_ROOT="$ANDROIDSDK"
    export ANDROID_HOME="$ANDROIDSDK"
    export ANDROID_NDK_HOME="$ANDROIDNDK"

    export PATH="$ANDROIDSDK/cmdline-tools/latest/bin:$ANDROIDNDK/toolchains/llvm/prebuilt/linux-x86_64/bin:$PATH"

    # --- use host compiler ---
    export CC=gcc
    export CXX=g++

    # --- autotools fixes for NixOS ---
    export ACLOCAL_FLAGS="-I ${pkgs.libtool}/share/aclocal -I ${pkgs.gettext}/share/aclocal -I ${pkgs.libffi}/share/aclocal"
    export ACLOCAL_PATH="${pkgs.libtool}/share/aclocal:${pkgs.gettext}/share/aclocal:${pkgs.libffi}/share/aclocal"

    # --- Python virtual environment ---
    if [ ! -d ".venv" ]; then
        python -m venv .venv
        echo "Created virtual environment in .venv"
    fi
    source .venv/bin/activate

    # --- install python-for-android in venv ---
    pip install --upgrade pip setuptools wheel
    pip install python-for-android

    export P4A_NO_SDK_MANAGER=1
    echo "Kivy + Python-for-Android nix-shell ready! Python-for-Android installed in .venv"
  '';
}
