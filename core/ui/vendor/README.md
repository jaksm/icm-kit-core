# vendor

Third-party code, bundled to a single import-free ESM file so the artifact needs no network.

## lit.js

Lit 3.3.3 plus the `classMap`, `repeat` and `unsafeHTML` directives. Rebuild with:

```bash
mkdir -p /tmp/litbuild && cd /tmp/litbuild && npm init -y && npm i lit@3
cat > entry.js <<'JS'
export * from "lit";
export {classMap} from "lit/directives/class-map.js";
export {repeat} from "lit/directives/repeat.js";
export {unsafeHTML} from "lit/directives/unsafe-html.js";
JS
npx esbuild entry.js --bundle --format=esm --minify --outfile=lit.js
```

Then copy `lit.js` here. It must stay a single file with no `import` statements: `build.py`
inlines it into the page and the artifact CSP would block a fetch.
