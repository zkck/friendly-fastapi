{
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = {
    self,
    nixpkgs,
    flake-utils,
  }:
    flake-utils.lib.eachDefaultSystem (system: let
      pkgs = import nixpkgs {
        inherit system;
      };
    in {
      devShells.default = pkgs.mkShell {
        buildInputs = [
          pkgs.uv
          pkgs.ruff
        ];
      };
      apps.format = let
        script = pkgs.writeShellScript "" ''
          ${pkgs.ruff}/bin/ruff check --extend-select I --fix
          ${pkgs.ruff}/bin/ruff format
        '';
      in {
        type = "app";
        program = script.outPath;
      };
      apps.lint = let
        script = pkgs.writeShellScript "" ''
          ${pkgs.ruff}/bin/ruff check .
        '';
      in {
        type = "app";
        program = script.outPath;
      };
    });
}
