{
  description = "a tool to view wikipedia pages from your terminal";

  inputs.nixpkgs.url = github:NixOS/nixpkgs/nixos-unstable;

  outputs = { self, nixpkgs }:
    let
      pkgs = import nixpkgs { system = "x86_64-linux"; };
      wik = pkgs.python3Packages.buildPythonPackage {
        pname = "wik";
        version = "1.4.0";
        pyproject = true;
        build-system = [pkgs.python3Packages.flit];
        src = self;
        propagatedBuildInputs = with pkgs.python3Packages; [ beautifulsoup4 requests ];
      };
    in {
      packages.x86_64-linux.default = wik;
    };
}
