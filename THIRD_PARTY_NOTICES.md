# Third-party code and data

No project-wide open-source reuse license has been selected for the original application code in this publication. The following third-party terms remain applicable to their respective files and dependencies.

## Bundled files

| Component | Files | Terms and attribution |
| --- | --- | --- |
| Leaflet 1.9.4 | `static/vendor/leaflet/` | BSD-2-Clause. The upstream copyright and license are retained in [LICENSE](static/vendor/leaflet/LICENSE). [Upstream license](https://github.com/Leaflet/Leaflet/blob/v1.9.4/LICENSE). |
| Pillow-derived image processing notice | `static/vendor/photo/PILLOW-LICENSE.txt` | The existing notice is retained with the browser processing source. [Pillow license](https://github.com/python-pillow/Pillow/blob/main/LICENSE). |
| Protected-species list | `data/protected_species.json` | Source: [Ministry of the Environment, Japan](https://www.env.go.jp/nature/kisho/domestic/list.html). Converted into JSON by the ikimono-note project. The bundled data declares its historical reference date; it is not asserted to be the latest list. [Ministry reuse terms](https://www.env.go.jp/mail.html), [Public Data License 1.0](https://www.digital.go.jp/resources/open_data/public_data_license_v1.0). |

## Installed dependencies

Dependencies are installed separately using `requirements.txt` and `requirements-dev.txt`; their distributions and transitive dependency notices are not repackaged here. The local browser capture uses original generated test artwork, a synthetic key, and fixed responses. No external biological photographs, model weights, map tiles, personal records, or real credentials are bundled in the walkthrough.

The public application can contact external AI, taxonomy, map, and Google services when those features are used. Publishing this source does not grant API access, guarantee a free hosted allowance, or change those services' terms.

Development dependencies reviewed on 2026-10-14: pytest (MIT), Playwright (Apache-2.0). See the [publication license record](docs/publication-license-review.json) for version-specific evidence and restrictions.
