# feh-data

Files were served directly from Github and Github does not deliver files over HTTP that are more than ~4Mo. So I had to obfuscate some long keys of my payloads as a workaround. You can find the list of those keys [there](https://github.com/matxx/feh-peeler/blob/main/utils/types/obfuscated-keys.ts).

Nowadays files are uploaded to S3 and served via Cloudfront but I never stopped using those obfuscated keys.

## Prompts to fix weapon restrictions with Claude

```
1. explore `data/skills.json`
2. find all skills without weapon restrictions : `"weapons": null`
3. check on the wiki via API (exemple: https://feheroes.fandom.com/api.php?action=query&titles=Ice_Edge&prop=revisions&rvprop=content&format=json) what are the correct restrictions and fill them in
```

```
Nice job, now commit your work on `data/skills.json`
```
