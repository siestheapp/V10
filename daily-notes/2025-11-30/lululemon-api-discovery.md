# Lululemon PDP API Discovery (2025-11-30)

## Source Signals Collected
- `__NEXT_DATA__` payloads for PDP `prod11500060` and men's dress pants category page. They confirm:
  - `configs.graphqlUrl` → `https://shop.lululemon.com/api/graphql`.
  - `pageProps.dehydratedState.queries` includes `['pdp', '<product_code>', 'v1']` entries containing all specs (care/fabric/features) required by `ingest_checker`.
  - `productAttributes.productContent{Care,Fabric,Feature}` already map cleanly to `core.product_specs` requirements.
- `rvmOverrides.subapps` exposes module-federation versions, e.g. `pdp-app` `2.3.57`, `cdp-app` `2.3.16`.
- Remote entry URLs therefore follow `https://shop.lululemon.com/static/uf/<subapp>/<version>/static/chunks/remoteEntry.js`.
- Akamai blocks simple `curl` downloads. Successful approach: load remote entry via a real browser session (Cursor browser tool) which saves content to `~/.cursor/browser-logs/snapshot-2025-11-30T05-22-45-226Z.log` for offline analysis.

## Reverse-Engineering Plan
1. **Map Remote Modules**
   - Use `rvmOverrides.subapps` to enumerate all micro-frontends (pdp, cdp, size-guide, layout, etc.) and their versions.
   - For each subapp, fetch `remoteEntry.js` via Playwright (same pattern as `lululemon_pdp_dump.fetch_html_via_playwright`) to avoid Akamai.
   - Store the JS locally under `data/tmp/remotes/<subapp>-<version>.js` for repeatable parsing.

2. **Locate GraphQL Clients**
   - Search the remote entry bundle for `fetch("/api/graphql"` or the literal persisted query hashes (`sha256Hash`) to recover `operationName` (e.g., `PdpProductQuery`).
   - Identify the React Query hook or data loader that populates the `['pdp', '<code>', 'v1']` cache node. That function should expose variables like `locale`, `productId`, `colorCode`.
   - Document the exact POST payload (likely `{operationName, variables, extensions: {persistedQuery: {version: 1, sha256Hash}}}`).

3. **Reproduce Requests**
   - Implement a thin client (e.g., `scripts/lululemon_graphql_client.py`) that accepts `operation_name`, `hash`, and variables, and posts to `https://shop.lululemon.com/api/graphql` with browser-like headers + `akamai` cookies from an initial GET (`https://shop.lululemon.com/`).
   - Validate by fetching `prod11500060` data and comparing to the stored `__NEXT_DATA__` payload.

4. **Integrate with Ingest**
   - Extend `lululemon_full_ingest.load_payload` to accept either (a) direct JSON file (current fallback) or (b) `--pdp-graphql <product_code>`. The latter should call the new client and rehydrate the same structure the rest of the script expects.
   - Future: expose category-level GraphQL query once we locate the `CategoryPageDataQuery` persisted hash so `lululemon_category_ingest` can avoid HTML dumps entirely.

## Next Actions
- [ ] Parse `data/tmp/lululemon_prod11500060.json` to dump the exact shape expected by `ingest_checker` (already confirmed for specs + marketing story).
- [ ] Build Playwright helper to fetch remote entries safely and save them locally.
- [ ] Grep remote bundles for `persistedQuery` metadata to recover hashes + operation names.
- [ ] Prototype a POST to `/api/graphql` with one persisted query once the hash is known.
