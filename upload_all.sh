#!/usr/bin/env ruby

require 'aws-sdk-s3'

secrets = JSON.load(File.read('secrets.json'))
Aws.config[:region] = secrets['Region']
Aws.config[:credentials] = Aws::Credentials.new(
  secrets['AccessKeyId'],
  secrets['SecretAccessKey']
)

hash = `git rev-parse HEAD`.strip

Dir['data/*.json'].each do |filename|
  Aws::S3::Object.new('feh-data', "#{hash}/#{filename.gsub(%r{\Adata/}, '')}").upload_file(filename)
end

