# Digital Product Passport (DPP) — Progress Notes

_Last updated: 2026-05-07_

---

## What was built

### Brick library: `shared_libraries/bricks/toy_dpp/`

Three bricks conforming to the `SHACLBrick` dataclass format
(`leaf_properties` list, `template_type`, `namespace: "dpp"`):

| File | Brick | Properties |
|---|---|---|
| `economicoperator_a1b2c3d4-0001-...json` | `EconomicOperator` | 8 — legal name, address fields, unique operator ID, email, URL |
| `notifiedbody_a1b2c3d4-0002-...json` | `NotifiedBody` | 4 — name, body number, certificate reference, certificate URL |
| `toydigitalproductpassport_a1b2c3d4-0003-...json` | `ToyDigitalProductPassport` | 16 — all Annex VI Part I mandatory fields (a–n) + 2 Part II optional fields |

Regulatory basis: **EU Toy Safety Regulation, Article 20 + Annex VI**.

### New presets — `shared_libraries/bricks/templates/_presets.json`

Six DPP-specific presets added:
- `Unique Product Identifier` — `schema:productID`, `xsd:string`, 1..1
- `Unique Operator Identifier` — `schema:identifier`, `xsd:string`, 1..1
- `Commodity Code` — `schema:identifier`, `xsd:string`, 0..1
- `Certificate Reference` — `schema:identifier`, `xsd:string`, 1..1
- `Safety Gate Portal URL` — `schema:url`, `xsd:anyURI`, 1..1
- `Boolean Flag` — `xsd:boolean`, 1..1  _(used for `CE Marking Present`)_

### Schema + SHACL/DASH output — `shared_libraries/schemas/toy_dpp/`

| File | Purpose |
|---|---|
| `toy-dpp-schema-001.json` | Schema loadable by `schema_app_v2` (library: `toy_dpp`) |
| `toy-dpp-schema-001.ttl` | SHACL + DASH Turtle — the authoritative output artefact |

The TTL contains:
- Standard prefixes (`sh:`, `xsd:`, `rdfs:`, `dash:`) + `dpp: <https://ec.europa.eu/dpp/toy#>` + `schema: <https://schema.org/>`
- `dpp:ToyDigitalProductPassport` — 16 leaf `sh:property` blocks with `sh:minCount`, `sh:maxCount`, `sh:description`, `dash:singleLine`
- Three `sh:node` edges from the passport to child shapes:

  | Edge path | Target shape | Cardinality | Annex ref |
  |---|---|---|---|
  | `schema:manufacturer` | `dpp:EconomicOperator` | 1..1 | Part I (b) |
  | `schema:accountablePerson` | `dpp:EconomicOperator` | 0..1 | Part I (c) — omit if same as manufacturer |
  | `schema:certification` | `dpp:NotifiedBody` | 0..* | Part I (j) |

- `dpp:EconomicOperator` — 8 leaf properties
- `dpp:NotifiedBody` — 4 leaf properties

---

## Pending work

### 1. Fix `dash_integration.py`
`schema_app_v2/core/dash_integration.py` still uses the old `object_type` /
`properties`-dict model. It will not correctly render a DASH HTML form from
these bricks. Needs updating to use `leaf_properties` list and `template_type`
instead of `brick.object_type`, `brick.properties`, `brick.constraints`.

### 2. Review the TTL output
Open `shared_libraries/schemas/toy_dpp/toy-dpp-schema-001.ttl` and verify:
- Property paths look correct (several reuse `schema:description` and
  `schema:identifier` with different labels — that is intentional but
  worth a second look against the regulation text).
- `dash:singleLine` is present on single-line fields and absent on
  multi-line text fields (description, instructions of use).

### 3. Consider authorised-representative brick
Currently the `EconomicOperator` brick is reused for all three operator
roles (manufacturer, responsible operator, authorised representative).
If the authorised representative needs additional fields (e.g. mandate
reference), it should become its own brick.

---

## Key lesson — hand-written brick JSON format

Bricks **must** use the `SHACLBrick` dataclass fields. The critical ones:

```json
{
  "brick_id": "<uuid>",
  "name": "MyBrick",
  "description": "...",
  "template_type": "free_text",
  "namespace": "dpp",
  "target_class": "https://schema.org/Product",
  "leaf_properties": [
    {
      "path": "https://schema.org/name",
      "label": "Name",
      "datatype": "xsd:string",
      "node_kind": null,
      "in_values": [],
      "has_value": null,
      "min_count": 1,
      "max_count": 1,
      "description": "...",
      "min_inclusive": null,
      "max_inclusive": null,
      "single_line": true
    }
  ],
  "xone_alternatives": [],
  "tags": [],
  "created_at": "...",
  "updated_at": "...",
  "metadata": {}
}
```

**Do not use** `object_type`, `properties` (dict), `constraints` (list at
brick level), `targets`, or `property_path` — `SHACLBrick.from_dict()` filters
them out silently, so the brick loads as empty.
