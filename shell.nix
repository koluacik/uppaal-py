{ pkgs ? import <nixpkgs> {} }:
let
  myEnv = pkgs.poetry2nix.mkPoetryEnv {
    python = pkgs.python38;
    projectDir = ./.;
    editablePackageSources = {
      uppaal-py = ./lib;
      tests = ./.;
    };
  };
in myEnv.env
