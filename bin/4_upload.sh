#!/usr/bin/env ruby

require 'aws-sdk-s3'

Aws.config[:region] = ENV.fetch('FEH_S3_REGION')
Aws.config[:credentials] = Aws::Credentials.new(
  ENV.fetch('FEH_S3_ACCESS_KEY_ID'),
  ENV.fetch('FEH_S3_SECRET_ACCESS_KEY'),
)

hash = `git rev-parse HEAD`.strip

bucket_name = ENV.fetch('FEH_S3_BUCKET_NAME')
tm = Aws::S3::TransferManager.new
Dir['data/*.json'].each do |filename|
  tm.upload_file(
    filename,
    bucket: bucket_name,
    key: "commits/#{hash}/#{filename.gsub(%r{\Adata/}, '')}",
    content_type: 'application/json',
  )
end

puts hash
