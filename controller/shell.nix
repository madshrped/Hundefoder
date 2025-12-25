{
  pkgs ? import <nixpkgs> { },
}:

let
  myDeps = with pkgs; [
    python313
    arduino-cli
    arduino-ide
    screen
    esptool
  ];
in
pkgs.mkShell {
  buildInputs = myDeps;

  shellHook = ''
    export LD_LIBRARY_PATH=${pkgs.lib.makeLibraryPath myDeps}:$LD_LIBRARY_PATH
    alias ac="arduino-cli"
    ac core update-index
    ac core install esp32:esp32
  '';

}
