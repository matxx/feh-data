#!/usr/bin/env ruby

require 'aws-sdk-s3'

Aws.config[:region] = ENV.fetch('FEH_S3_REGION')
Aws.config[:credentials] = Aws::Credentials.new(
  ENV.fetch('FEH_S3_ACCESS_KEY_ID'),
  ENV.fetch('FEH_S3_SECRET_ACCESS_KEY'),
)

hash = `git rev-parse HEAD`.strip

bucket = Aws::S3::Bucket.new(ENV.fetch('FEH_S3_BUCKET_NAME'))
Dir['data/*.json'].each do |filename|
  bucket
    .object("commits/#{hash}/#{filename.gsub(%r{\Adata/}, '')}")
    .upload_file(filename, content_type: 'application/json')
end

puts hash
