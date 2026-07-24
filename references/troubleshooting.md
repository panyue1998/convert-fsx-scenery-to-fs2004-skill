# Preventive Checks, Runtime Diagnosis, And Proven Decisions

Run the first six sections as build-time gates on every conversion. Do not wait for the user to report missing airport data, wrong elevation, white textures, inverted textures, material mismatch, or short ground draw distance. The rectangular-shadow section remains a runtime diagnosis because FS2004's renderer decides that behavior.

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

## Prevent White Ground Textures

Cause: legacy ground BGL embeds `.dds` names while FS2004 output contains `.bmp`, or BMP encoding is unsupported.

Mandatory build-time action:

- Export the ground BGL as `SCA_GP`.
- Rewrite quoted `.dds` references to `.bmp` with `rewrite_sca_textures.py`.
- Compile with SCASM and verify no final BGL contains `.dds` strings.
- Verify each BMP uses DXT1/DXT3 extended BMP encoding and power-of-two dimensions no larger than 1024.

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
- Do not remap UV coordinates automatically unless the converted geometry demonstrably differs from the source.

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

## Prevent Wrong Building Angles Or Positions

Cause: FSX placement binary decoding used the wrong heading/pitch/bank unit conversion, ignored AGL/MSL altitude semantics, swapped coordinates, or lost scale.

Mandatory build-time action:

- Preserve lat/lon/altitudeIsAgl/alt/heading/pitch/bank/scale from the decoded placement record.
- Validate several known buildings against the source placement data before compiling the final placement BGL.
- Treat a systematic rotation or offset as a placement-decoder bug. Fix the conversion math and rebuild the placement BGL; do not manually rotate individual buildings unless only one source placement is demonstrably wrong.

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
- Day/night textures and alpha render correctly.
- Test once with ground scenery shadows enabled and once disabled.
- Restart FS2004 after replacing BGLs to avoid judging cached scenery.
