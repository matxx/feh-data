#!/usr/bin/env ruby

require 'aws-sdk-s3'

Aws.config[:region] = ENV.fetch('FEH_S3_REGION')
Aws.config[:credentials] = Aws::Credentials.new(
  ENV.fetch('FEH_S3_ACCESS_KEY_ID'),
  ENV.fetch('FEH_S3_SECRET_ACCESS_KEY'),
)

bucket = Aws::S3::Bucket.new(ENV.fetch('FEH_S3_BUCKET_NAME'))
bucket.objects(prefix: 'exports').each do |obj|
  next if obj.key.include?('errors')

  bucket.object(obj.key).download_file("data/#{File.basename(obj.key)}")
end
