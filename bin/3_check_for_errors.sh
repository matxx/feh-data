#!/usr/bin/env ruby

errors = Hash.new { |h, k| h[k] = Hash.new(0) }
[
  'data/skills.json',
  'data/seals.json',
].each do |file|
  str = File.read(file)
  errors[file][:no_weapon_restriction]    += str.scan(/"weapons": null/).size
  errors[file][:empty_weapon_restriction] += str.scan(/"can_use": \[\]/).size
end

if errors.any?
  lines = []
  errors.each do |file, errs|
    lines << "- erreurs dans le fichier : #{file}"
    lines << %{-- #{errs[:no_weapon_restriction]}" sans restriction (`"weapons": null`)}
    lines << %{-- #{errs[:empty_weapon_restriction]}" aucune restriction (`"can_use": []`)}
  end
  puts lines.join("\n")
end
