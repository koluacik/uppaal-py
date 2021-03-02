{ pkgs ? import <nixpkgs> {} }:
let
  myEnv = pkgs.poetry2nix.mkPoetryEnv {
    projectDir = ./.;
    editablePackageSources = {
      uppaal-py = ./lib;
      tests = ./.;
    };
  };
in myEnv.env
