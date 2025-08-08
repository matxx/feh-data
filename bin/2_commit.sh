#!/usr/bin/env ruby

require 'date'

if `git status --porcelain`.split("\n").any? { |line| line.include?('data/') }
  `git commit data/* -m "chore: #{Date.today.strftime('%Y-%m-%d')} update"`
  `git push origin`
end
