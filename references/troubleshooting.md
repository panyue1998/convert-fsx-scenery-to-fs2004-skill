# Preventive Checks, Runtime Diagnosis, And Proven Decisions

Apply the relevant prevention sections as build-time gates during their governing workflow steps. Do not wait for the user to report missing airport data, wrong elevation, white textures, inverted textures, material mismatch, or short ground draw distance. The rectangular-shadow section remains a runtime diagnosis because FS2004's renderer decides that behavior.

## Prevent Missing Airport List Entry Or Surfaces

Cause: the airport-definition BGL was skipped as terrain/unknown, or NewBglAnalyze produced incomplete XML.

Mandatory build-time action:

1. Inspect all plausible BGLs in ADE, including misleadingly named CVX files.
2. Export complete XML manually from ADE when analyzer output lacks runway, taxiway, parking, apron, communications, approaches, ILS, or navaid records expected from the scenery.
3. Compile that XML with FS2004 BGLComp and verify the ICAO airport appears in the FS2004 list.
4. Never synthesize missing facilities from a partial analyzer dump.

## Prevent Underground Buildings Or Missing Flatten

Cause: FSX terrain/CVX flatten does not survive the conversion, or placement altitude/elevation is inconsistent.

Mandatory build-time action:

- Confirm airport elevation from complete airport XML and model placements.
- Build a conservative FS2004-compatible flatten covering the airport operational area at that elevation.
- Test terminal and apron elevations. Do not shift every model to hide one bad placement.
- Check first-loaded airport datum and curved ground vertices separately; a correct flatten can still cover below-plane polygons at close range. See [ground curvature and height](geometry-texture-audits.md#ground-curvature-and-height).

## Prevent White Ground Textures

Possible causes: legacy `.dds` references versus output `.bmp`, unsupported encoding, lost meaningful BMP alpha or an unintended visible overlay. White polygons do not prove missing files.

Mandatory build-time action:

- Export the ground BGL as `SCA_GP`.
- Rewrite quoted `.dds` references to `.bmp` with `rewrite_sca_textures.py`.
- Compile with SCASM and verify no final BGL contains `.dds` strings.
- Verify each BMP uses DXT1/DXT3 extended BMP encoding and power-of-two dimensions no larger than 1024.
- Audit raw BI_RGB32 alpha and intentionally invisible seasonal placeholders, then check compressed alpha independently. ImageTool can discard all-zero TGA alpha. Follow [texture alpha and orientation](geometry-texture-audits.md#texture-alpha-and-orientation) before hiding AFCAD surfaces or changing parking widths.

## Prevent Upside-Down Textures

Cause: FSX DDS and FS2004 extended BMP use different vertical texture origins in this workflow.

Mandatory build-time action: vertically flip every DDS before ImageTool encoding. Check text-bearing textures such as terminal signs and billboards; do not selectively flip only textures noticed by the user.

## Prevent Texture/Surface Mismatch

Possible causes: a texture stem collision, changed filename, incorrect model/material conversion, missing texture, or inconsistent orientation.

Mandatory build-time action:

- Preserve every source texture stem and compare model material references against output filenames.
- Detect duplicate stems before conversion.
- Inspect a DAE export and material list for the affected model.
- Confirm day and `_LM` textures remain paired.
- Verify immutable shared-offset remapping and original attribute lineage through multiple splits. A position pass can hide UV corruption; use [joint attribute checks](geometry-texture-audits.md#immutable-shared-index-splitting). Do not guess UV offsets or flip UVs to compensate for unverified texture orientation.

## Prevent Missing Buildings

Cause: object library BGLs were converted but their FSX placement records were not rebuilt for FS2004, or placement GUIDs no longer match the converted library GUIDs.

Mandatory build-time action:

1. Decode every plausible placement BGL and recover each `LibraryObject` GUID, position, altitude mode, heading, pitch, bank, and scale.
2. Match raw placement GUID bytes against final FS2004 library BGLs; do not rely only on filename similarity.
3. Compile recovered placements into FS2004 BGLComp XML/BGL outputs, keeping airport-area and city-area placements separate for easier rollback.
4. Report every source placement whose GUID has no final library match, and every converted library that has no placement.

## Prevent Transparent Or Incorrectly Textured Buildings

Cause: MCX/MakeMDL material conversion changed alpha mode, reordered materials, lost `_LM` pairing, used a renamed texture stem, or consumed DDS/BMP inputs with the wrong vertical origin.

Mandatory build-time action:

- Compare exported source and final material lists for terminal, cargo, hotel, city, and sign-bearing models.
- Preserve source texture stems exactly and keep day/night pairs.
- Use vertically flipped FS2004 BMP inputs for converted models; do not mix unflipped source DDS with already-flipped BMPs in the same rebuild pass.
- Inspect at least one text-bearing and one alpha/cutout building after conversion. If walls, roofs, glass, or signs use the wrong bitmap, recompile the affected library before packaging.

### Do not infer transparency from DDS alpha

An alpha channel is data, not proof that the surface should be transparent. FSX materials may ignore alpha or use it for another rendering function, while a DAE/MakeMDL rebuild can silently reinterpret the same zero-alpha pixels as holes.

Mandatory procedure:

1. Decode every source texture to RGBA and count alpha `0`, alpha `1..254`, and alpha `255` pixels.
2. Map each non-opaque texture through the source material to the exact model and surface. Inspect source blend, alpha-test, transparency, and double-sided flags.
3. Classify the surface explicitly: opaque architecture, cutout fence/vegetation, glass, light sprite, or unknown. Stop on unknown high-area architectural alpha.
4. For opaque architecture, preserve RGB but force alpha to `255` in a model-specific day/`_LM` copy, or rebuild the material with verified opaque semantics. Do not change the shared source-stem texture if another model legitimately uses its alpha.
5. For cutouts, keep alpha and verify the fence/vegetation silhouette. Never make all textures in a composite model opaque.
6. Inspect the final DXT payload, not only the header: count DXT1 selector-3 transparent pixels or decoded DXT3 alpha. Require zero for opaque surfaces.

Proven failure: `Cargo_Hangars_01` and `Cargo_Hangars_02` contained source alpha even though their building surfaces were not intended to be cut out. Pixel-preserving DDS-to-BMP conversion retained the alpha correctly, but FS2004 then rendered holes. The correct prevention is material-intent classification before format selection, not assuming source alpha is authoritative.

## Prevent Wrong Building Angles Or Positions

Cause: FSX placement binary decoding used the wrong heading/pitch/bank unit conversion, ignored AGL/MSL altitude semantics, swapped coordinates, or lost scale.

Mandatory build-time action:

- Preserve lat/lon/altitudeIsAgl/alt/heading/pitch/bank/scale from the decoded placement record.
- Validate several known buildings against the source placement data before compiling the final placement BGL.
- Treat systematic rotation or offset as a conversion-math defect. Verify placement decoding and source/target projection before manual adjustments. An ECEF round-trip can still leave FS2004 seams displaced. Follow [coordinate frames and component coherence](geometry-texture-audits.md#coordinate-frames-and-component-coherence), including complete-object grouping and correct lamp/glow matching.

### Prevent airport-reference-point models from appearing over a runway

Some FSX scenery uses the airport reference point as the placement for a large model whose vertices are already offset to their real-world site. The placement record is correct, but FS2004 can render, cull, or position kilometre-distant local geometry incorrectly. Inspect model space as well as placement space.

Mandatory procedure:

1. Flag every single-model BGL whose lone placement equals or nearly equals the airport reference point, especially `VERY_SPARSE` objects and files representing roads, fences, or building rows.
2. Export the source BGL to DAE and calculate bounds from position arrays only; do not include normals, UVs, colors, or animation values.
3. Compute the local bounding-box center `(cx, cy)` and its distance from `(0,0)`. Investigate offsets of hundreds of metres; reject kilometre-scale offsets for direct FS2004 installation.
4. Convert the local center through the original placement heading. With local `x` east/right and `y` north/forward, use the verified model-axis convention from representative source placements; then convert using the verified source/target conventions in [the coordinate audit](geometry-texture-audits.md#coordinate-frames-and-component-coherence).
5. For pure translation within one frame, subtract the same `(cx, cy)` from every position array and preserve the other attributes. If changing frame/projection, transform positions and normals consistently while preserving UVs, materials, animation relationships and geographic footprint. Do not mix projection conversion with unexplained manual offsets.
6. Compile the recentered model under a new GUID and compile a separate placement at the transformed geodetic center. Preserve heading, scale, image complexity, and the intended AGL/MSL mode; usually use AGL `0` for a grounded rebuilt object after confirming the flatten.
7. Verify transformed min/max corners cover the intended site and no longer cross the runway. Audit adjacent reference-point BGLs for the same authoring pattern.

Proven failure: a roughly 707 m building row and a separate roughly 1.16 km fence/road model were both placed at the RKSS runway/airport reference point while their geometry centers were about 1.6 km away in model space. Direct conversion produced objects over the runway. Recentered models placed at their transformed centers restored the intended south-side building and fence corridor.

## Large Rectangular Shadow

Diagnostic: if the rectangle disappears when FS2004 `Ground scenery shadows` is disabled, it is a scenery-shadow artifact, not a texture, alpha, flatten, or airport XML problem.

Very wide, nearly flat models are likely contributors. Exporting confirmed flat models to SCASM ground polygons is a reversible experiment, but in the Nanyuan conversion changing both large candidates did not remove the rectangle. Therefore:

- Treat disabling FS2004 ground scenery shadows as the only verified workaround.
- Explain that this setting also disables shadows for other scenery objects.
- Do not attempt MakeMDL ASM/MDL shadow-section surgery without a separate experimental package and explicit user approval.
- Do not keep converting unrelated buildings after the first controlled test fails.

## Prevent Short Ground-Imagery Draw Distance

First distinguish mipmaps from object visibility.

1. Inspect final BMP dimensions, DXT compression, data size, and mip chain.
2. Inspect SCASM `RefPoint` values. MCX ground-polygon exports commonly use `v1=10000`, a 10,000 m visibility limit.
3. When mipmaps are present and default terrain appears abruptly near that range, use `adjust_sca_visibility.py` to change only the expected `v1` value.
4. Use 20,000 m as the tested moderate value, apply it to every ground-polygon SCA for the airport, compile all with SCASM, and preserve the previous BGL set in `work/backup`.
5. Do not globally replace label text such as `Return4_10000`; change only `v1` values.

Longer visibility increases rendering and texture-memory pressure. Start at 20 km rather than using an extreme value.

## Final Simulator Test Matrix

- Airport appears by ICAO in the airport list.
- Runway, starts, taxi network, parking, and aprons are present.
- Airport surface is flat at the intended elevation; buildings are not buried or floating.
- Ground imagery is visible, correctly oriented, correctly mapped, and present at the desired distance.
- Day/night textures and alpha render correctly, including invisible seasonal placeholders.
- Low/close views retain custom ground; vehicle bodies/interiors, building/glass seams and dusk/night lights remain aligned. File checks and projection estimates do not replace runtime observations.
- No airport-reference-point model has a suspicious far-from-origin geometry center; transformed footprints match their intended sites.
- Every non-opaque source texture has a recorded material-intent classification, and opaque architectural DXT payloads contain zero transparent pixels.
- Test once with ground scenery shadows enabled and once disabled.
- Restart FS2004 after replacing BGLs to avoid judging cached scenery.
