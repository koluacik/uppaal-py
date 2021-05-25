{ pkgs ? import <nixpkgs> {} }:
let
  myEnv = pkgs.poetry2nix.mkPoetryEnv {
    python = pkgs.python38;
    projectDir = ./.;
    editablePackageSources = {
      uppaal-py = ./lib;
    };
    overrides = pkgs.poetry2nix.overrides.withDefaults (self: super: {
      lazy-object-proxy = pkgs.python38Packages.lazy-object-proxy;
      decopatch = pkgs.python38Packages.decopatch;
      pytest-cases = pkgs.python38Packages.pytest-cases;
    });

  };
in myEnv.env
