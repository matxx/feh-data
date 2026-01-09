# feh-data

Files were served directly from Github and Github does not deliver files over HTTP that are more than ~4Mo. So I had to obfuscate some long keys of my payloads as a workaround. You can find the list of those keys [there](https://github.com/matxx/feh-peeler/blob/main/utils/types/obfuscated-keys.ts).

Nowadays files are uploaded to S3 and served via Cloudfront but I never stopped using those obfuscated keys.
