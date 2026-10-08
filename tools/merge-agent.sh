#!/usr/bin/env bash
# Kullanım: tools/merge-agent.sh gameplay   (mevcut dala birleştirir; çakışmada durur)
set -e
git merge --no-ff "agent/${1:?ajan adı gerekli}" || { echo "ÇAKIŞMA: kullanıcıya sor"; exit 1; }
