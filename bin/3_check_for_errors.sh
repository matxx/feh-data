#!/usr/bin/env ruby

errors = Hash.new { |h, k| h[k] = Hash.new(0) }
[
  'data/skills.json',
  'data/seals.json',
].each do |file|
  str = File.read(file)

  cnt = str.scan(/"weapons": null/).size
  errors[file][:no_weapon_restriction] += cnt if cnt > 0

  cnt = str.scan(/"can_use": \[\]/).size
  errors[file][:empty_weapon_restriction] += cnt if cnt > 0
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
