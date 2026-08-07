#!/usr/bin/env ruby

hash = `git rev-parse HEAD`.strip

# upload files to s3

require 'aws-sdk-s3'

Aws.config[:region] = ENV.fetch('FEH_S3_REGION')
Aws.config[:credentials] = Aws::Credentials.new(
  ENV.fetch('FEH_S3_ACCESS_KEY_ID'),
  ENV.fetch('FEH_S3_SECRET_ACCESS_KEY'),
)

bucket_name = ENV.fetch('FEH_S3_BUCKET_NAME')
tm = Aws::S3::TransferManager.new
Dir['data/*.json'].each do |filename|
  key = "commits/#{hash}/#{filename.gsub(%r{\Adata/}, '')}"
  tm.upload_stream(bucket: bucket_name, key:, content_type: 'application/json') do |write_stream|
    write_stream << JSON.dump(JSON.parse(File.read(filename)))
  end
end

# update local env variables

matxx_path = File.expand_path('~/matxx.sh')
content = File.read(matxx_path)
content.sub!(/^export FEH_PEELER_COMMIT_HASH=.*$/, "export FEH_PEELER_COMMIT_HASH=#{hash}")
File.write(matxx_path, content)

peeler_path = File.expand_path('../feh-peeler/.env')
content = File.read(peeler_path)
content.sub!(/^NUXT_PUBLIC_COMMIT_HASH=.*$/, "NUXT_PUBLIC_COMMIT_HASH=#{hash}")
File.write(peeler_path, content)

# update cloudflare worker secret

require 'net/http'
require 'json'
require 'uri'

account_id  = ENV.fetch('CLOUDFLARE_ACCOUNT_ID')
api_token   = ENV.fetch('CLOUDFLARE_API_TOKEN')
script_name = 'feh-peeler'

uri = URI("https://api.cloudflare.com/client/v4/accounts/#{account_id}/workers/scripts/#{script_name}/secrets")

req = Net::HTTP::Put.new(uri, {
  'Authorization' => "Bearer #{api_token}",
  'Content-Type' => 'application/json',
})
req.body = { name: 'NUXT_PUBLIC_COMMIT_HASH', text: hash, type: 'secret_text' }.to_json

res = Net::HTTP.start(uri.host, uri.port, use_ssl: true) { |http| http.request(req) }
raise "Cloudflare API error: #{res.code} #{res.body}" unless res.is_a?(Net::HTTPSuccess)

puts hash
