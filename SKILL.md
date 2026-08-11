---
name: convert-fsx-scenery-to-fs2004
description: Convert Microsoft Flight Simulator X scenery packages into non-destructive FS2004 scenery-library packages, including BGL downgrade, airport XML recovery, flatten creation, legacy ground polygons, DDS-to-extended-BMP textures, visibility tuning, object-triggered global texture-blur diagnosis, and validation. Use for FSX-to-FS2004 scenery conversion or repair requests in either Chinese or English.
---

# Convert FSX Scenery To FS2004

Create a separate, runnable FS2004 package. Prefer stable omissions over unsafe conversion.

## Language

- Detect whether the user writes in Chinese or English and conduct the entire interaction in that language.
- When useful, show an unfamiliar tool or menu name as `中文 / English`; do not force bilingual duplication into every message.
- Translate errors and instructions, but preserve literal paths, filenames, commands, XML element names, and log text.

## Mandatory Start: Tools And Paths

Do not run conversion first. Begin by explaining the required tools and ask the user to install missing components and provide paths in one grouped request.

Require and verify:

1. FS2004 BGLComp SDK: `BGLComp.exe`, `bglcomp.xsd`.
2. FS2004 MakeMDL SDK: `MakeMDL.exe`, `modeldef.xml` or the supplied parts XML.
3. FS2004 Terrain SDK: `ImageTool.exe`.
4. ModelConverterX and its `ModelConverterX.dll`.
5. ADE 1.78 or compatible, for complete airport XML recovery.
6. NewBglAnalyze/BGLAnalyze, useful but not authoritative when output is incomplete.
7. SCASM, normally bundled with MCX or ADE.
8. .NET Desktop Runtime required by MCX, plus Python with Pillow and pywinauto.
9. DXTBmp, optional for manual texture inspection.
10. Source scenery path and a distinct output path.

Explicitly confirm that BGLComp, MakeMDL, and ImageTool are FS2004 versions. Reject an output path equal to the source or its `Scenery`/`Texture` folders. Read [references/toolchain.md](references/toolchain.md) for path prompts and checks.

## Conversion Workflow

1. Inventory and hash all source files. Never delete, rename, move, or overwrite source files.
2. Create an output root with `scenery`, `texture`, `work`, and `logs`. Put backups and intermediate files only below `work`.
3. Classify every BGL before conversion as object/placement, airport, terrain/CVX, or legacy ground polygon. Record the decision for every file.
4. Recover and verify the complete airport definition before compiling general objects. Treat NewBglAnalyze output as provisional; compare counts for runway, starts, taxi points/paths, parking, aprons, communications, approaches, ILS, and navaids. Require ADE XML immediately when expected content is absent.
5. Compile the verified airport XML with FS2004 BGLComp. Confirm the ICAO, runway geometry, airport elevation, and magnetic variation are plausible; correct only demonstrably invalid values.
6. Audit elevation before object conversion. Compare airport elevation, flatten elevation, and every placement's AGL/MSL mode. Recreate a conservative FS2004 flatten when the FSX CVX flatten cannot be compiled; do not wait for buried or floating buildings to appear in FS2004.
7. Inventory texture stems case-insensitively and fail on collisions. Extract model material references, verify every referenced day/night texture has a unique output target, and preserve stems exactly.
8. Convert every DDS to vertically flipped, maximum 1024-pixel, DXT1/DXT3 extended BMP with a complete mip chain. Verify headers, dimensions, alpha mode, mip payload, and `_LM` pairing before model installation.
9. Configure MCX with `scripts/configure_mcx.py`. Expect repeated MCX license/permission dialogs; automate only those dialogs. If automation fails, pause and guide the user to click the agreement buttons.
10. Run `scripts/convert_scenery.py` with explicit paths. Convert object BGLs as `BGL_9`; never copy a failed FSX-only BGL into final output.
11. Rebuild missing object placements before simulator testing. Extract placement records from FSX placement BGLs, map their raw GUID bytes to converted FS2004 library BGLs, and compile separate airport and city placement XML/BGL outputs with FS2004 BGLComp. Do not assume a converted library BGL is enough: a visible object needs both a converted library model and a valid FS2004 placement record.
12. Resolve user-reported objects by evidence, not names. When the user identifies an object by visual description, runway end, city side, direction, or relative position, parse placement XML/BGL coordinates, compute distance/bearing from known airport/runway landmarks, match placement GUIDs to model libraries, and only then edit or disable the confirmed placement or library. Do not infer the target from filename, texture name, or a visually similar model name alone.
13. Preserve FSX placement orientation exactly. Convert FSX placement heading/pitch/bank units into BGLComp degrees, keep `altitudeIsAgl` semantics, preserve scale, and validate representative airport and city objects against their source coordinates. If a batch of buildings is rotated or displaced, fix the placement conversion math before editing individual models.
14. Audit converted building libraries for material fidelity before installation. Export representative building BGLs to DAE/OBJ or MCX-readable reports, compare texture/material names with the FSX source, keep source stems and `_LM` pairings, and reject conversions whose materials become transparent, reordered, renamed, or assigned to the wrong surface. Recompile the affected library from source with corrected texture inputs instead of hiding the symptom by changing placements.
15. Export legacy ground polygons to SCA, rewrite embedded `.dds` references to `.bmp`, and compile with SCASM. Confirm final material references resolve to the converted BMP set.
16. Set ground-polygon visibility deliberately. Use 20,000 m as the tested starting value when the source export contains `v1=10000`; apply it consistently to all airport ground-polygon SCA files.
17. Proactively inspect large or nearly flat object BGLs as DAE before final installation. Classify true ground-detail models separately from buildings, but do not assume this removes FS2004 shadow artifacts.
18. Run `scripts/validate_package.py` and complete every required build-time gate below before asking the user to test FS2004.

## Optional: One Object Triggers Global Texture Blur

Use this first when an object entering the view, especially at a distance, makes unrelated FS2004 textures across the scene suddenly drop to very low resolution.

1. Before resizing ordinary large textures or bisecting every BGL, scan every active BMP in the target package. Rank candidates primarily by having only one usable mip level, a declared mip count or image size that disagrees with the actual payload, incomplete/extra mip data, or heavy repeated UV use across many model triangles. Use unusually small or narrow dimensions only as an additional risk signal, never as a fixed cutoff. Scan the whole package, not only the reported area.
2. Map each candidate BMP through model material references to its library BGL and placement GUID. Treat the combined structural and usage profile as a candidate signal, not proof; filenames or dimensions alone are insufficient.
3. Make the first simulator experiment a direct, non-destructive BMP disable. Move or rename all high-confidence candidates into a package-local holding folder, keep their BGLs active, archive/remove only the package-local `SCENERY.dat`, and restart FS2004 completely. Missing-material surfaces may turn white; that is expected and does not invalidate the test.
4. If global blur disappears, restore candidates individually or by recorded binary search until each offender is confirmed. Assume multiple independent BMPs may exist: one positive isolated test does not prove it is the only offender. Confirm both directions when practical: the BMP enabled can trigger blur, and the full package with that BMP disabled remains clear.
5. After confirmation, either leave the BMP disabled with documented visual loss, or rebuild it under the identical filename and aspect ratio as a power-of-two DXT1/DXT3 extended BMP no larger than 1024 with a usable mip chain. Retest before accepting the rebuild.
6. If disabling all structural candidates does not clear the symptom, restore them and continue with recorded BGL binary search and model/material inspection. Do not keep destructive or unlogged trial states.

A proven example is a `4x64` or `8x4` DXT1 BMP with only one mip, used with heavily repeated UVs across a substantial model part. These dimensions are examples, not thresholds: apply the same checks to any size when mip structure, payload declarations, and UV usage are suspicious. Such a texture can be valid-looking and fully decodable yet still provoke FS2004's global texture-resolution collapse at distance.

## Optional: Remove One Airport From A Directory

Use this when the user asks to delete, hollow out, or exclude all scenery content for a specific airport inside a package or converted output while preserving other airports in the same directory.

1. Confirm the exact target directory, airport identifiers, names, and approximate coordinates. Search for all likely codes and names, but treat text hits as leads only.
2. Inventory all candidate BGLs in the requested directory. Classify each hit as airport/AFCAD, object placement, model library, terrain/vector, nav database, or overlay patch. Do not modify files outside the requested directory without explicit permission.
3. For mixed-cell airport BGLs, do not disable the whole file when it contains other airports. Parse or decompile the airport section, remove the target airport from the airport list/namelist index, and preserve unrelated airport records. Validate with ADE or a name-list probe that the target airport is gone and unrelated airports remain.
4. Compile a local `DeleteAirport` overlay with FS2004 BGLComp for the target ident and coordinates, setting the relevant `deleteAll*` flags for runways, taxiways, starts, aprons, frequencies, approaches, and lights. If a normal overlay suppresses default runways but re-adds the airport to the map/list, keep the `DeleteAirport` record and section structure but patch its namelist airport/ICAO display counts to zero. If needed, remove the airport `NAME` subrecord and clear unused namelist strings while preserving the delete record and any exclusion section.
5. Remove local buildings and scenery objects by parsed coordinates, not by filename guesses. For object BGLs, identify placements within a small bounding box around the airport or by distance/bearing from runway landmarks, then remove or exclude only the confirmed target placements. Use an `ExclusionRectangle` only when it is narrow enough to avoid unrelated scenery.
6. Keep source and output originals non-destructive: back up touched output BGLs under `work/backup` or `_codex_repair`, disable superseded patches with `.off_YYYYMMDD_HHMMSS`, and force only the package-local scenery index to rebuild when present.
7. Validate all three surfaces separately: ADE airport list has no target airport, FS2004 map/list has no target ident/name, and the simulator no longer shows default runway/building remnants. Record rollback steps and any remaining global nav database hits that were intentionally not modified.

## Required Build-Time Gates

Do not defer these checks to user-reported debugging:

- **Airport completeness:** compile only from XML whose facility counts match the visible source airport; verify ICAO and nonzero required records.
- **Elevation:** install an FS2004-compatible flatten at the confirmed elevation and audit AGL/MSL placement semantics.
- **Texture availability:** ensure every final model/ground texture reference resolves case-insensitively to exactly one BMP.
- **Texture orientation:** flip all source DDS files during conversion and inspect representative text-bearing textures before packaging.
- **Material integrity:** compare source/exported material names and day/night pairs; do not rename, merge, or deduplicate unrelated textures.
- **Building completeness:** for every source building/terminal/object library and placement BGL, record whether the final package contains a matching FS2004 library BGL and a compiled placement BGL. Treat missing terminal/city buildings as a build failure unless the skip is explicit and documented.
- **Building material fidelity:** inspect representative terminal, cargo, hotel, city, and vegetation/cutout models for wrong transparency, wrong face texture assignment, missing `_LM`, and upside-down text. Fix material conversion and texture preparation before accepting the package.
- **Placement orientation and position:** compare source and final lat/lon/alt/heading/pitch/bank/scale for sampled airport and city objects. Treat global rotation, mirrored heading, or systematic offset as a conversion bug in placement decoding, not as a manual per-building adjustment.
- **Object targeting evidence:** for any user-reported object or direction-specific issue, document the parsed coordinates, distance/bearing to a known landmark, placement GUID, matched model library, and exact BGL/XML record before changing it. Filename or texture-name similarity alone is not enough evidence.
- **Ground format:** rewrite all embedded ground `.dds` references, compile with SCASM, and verify final BGLs contain no `.dds` strings.
- **Mipmaps and distance:** verify complete mip chains independently from SCA `v1` visibility; prioritize single-mip BMPs, mip declaration/payload inconsistencies, and heavy model UV repetition, using unusual dimensions only as supporting evidence; use 20 km unless the user requests another tested value.
- **Package integrity:** require unchanged source hashes, nonempty BGLs, valid extended BMP headers, clean compiler logs, and documented skips.

## Human-Assisted Steps

When a GUI step is needed, stop automation, explain why, give numbered instructions in the user's language, state the exact output path/filename to create, and state how completion will be verified. Continue only after the user confirms completion or the expected file appears.

Use [references/manual-steps.md](references/manual-steps.md) for ADE airport XML export, MCX permission dialogs, and DXTBmp inspection. Never imply that NewBglAnalyze succeeded merely because it produced a file.

## Preventive Checks And Runtime Exceptions

Read [references/troubleshooting.md](references/troubleshooting.md) during the initial build, not only after a failed simulator test. Apply its airport, elevation, texture, material, ground-format, and visibility checks proactively. Use runtime diagnosis only for engine-dependent behavior such as shadows.

The reference records the proven handling for:

- airport missing from the FS2004 list or missing runway/apron/taxi data;
- incorrect building elevation and missing flatten;
- white ground textures;
- vertically inverted signs and advertisements;
- textures mapped onto the wrong surfaces;
- large rectangular ground-scenery shadows;
- ground imagery appearing only near the airport.
- an object entering view and collapsing global texture resolution because of a suspicious single-mip or payload-inconsistent BMP combined with repeated UVs.

## Safety And Acceptance

- Preserve all source hashes and keep every replaced output BGL in `work/backup`.
- Do not remove unsupported content from the source. Record skipped files and reasons.
- Do not perform undocumented MDL/ASM shadow surgery.
- Accept a package only when validation reports `valid: true`, source hashes are unchanged, BGLs are nonempty, BMP headers are FS2004-compatible, no final BGL references `.dds`, and the airport passes an in-simulator smoke test.

## Bundled Scripts

- `scripts/configure_mcx.py`: configure FS2004 compiler paths for MCX.
- `scripts/convert_scenery.py`: perform guarded BGL and texture conversion.
- `scripts/inspect_bgl.py`: export BGLs and optionally capture transient placement XML.
- `scripts/rewrite_sca_textures.py`: change SCA texture references from DDS to BMP.
- `scripts/adjust_sca_visibility.py`: safely change expected `RefPoint` visibility values.
- `scripts/validate_package.py`: validate source integrity and final package formats.
