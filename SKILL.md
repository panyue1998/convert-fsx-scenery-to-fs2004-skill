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

## Execution Discipline

- Execute the 23 numbered workflow steps below in their written order. Do not omit, merge, reorder, add, or replace steps on your own initiative. Record a result for every numbered step; when a conditional action is genuinely inapplicable, record it as not applicable with evidence instead of silently removing it.
- Do not invent extra conversion, repair, configuration, or validation steps. Perform a necessary correction inside the numbered step or required gate that governs it. Run an optional procedure only when its stated trigger is present; do not turn optional procedures into standard extra steps.
- Finalize and prevalidate XML, MDLs, GUIDs, placements, airport graphs, radio records, geometry, alpha intent, and `One/Zero` state before final BGLComp assembly. Prefer one successful final build, but necessary recompilation is allowed within the authorized conversion or repair: for example, to correct a compiler/path failure, a demonstrated defect, or accepted geometry/material/elevation changes. Do not request separate approval merely because a BGL was compiled before. Before each retry, identify the cause, apply and prevalidate a concrete correction, back up any existing output under `work/backup`, and retain every attempt's input hash, command, complete log, return code, and outcome in the invocation manifest. Check error text and actual model/placement content as well as the exit code; an empty-header BGL or an error log is a failed build even if exit code is zero. Stop repeating an identical failed attempt: investigate or change the approach first. Keep provisional syntax/material checks at XML/MDL level rather than routinely assembling probe BGLs, and rerun every gate affected by a necessary final rebuild.
- After conversion execution begins, remain in the same active session until every non-human step and required validation is complete. Do not end with a progress-only response, ask the user to say “continue,” or stop because a command is long-running, a compiler fails, or a retry is needed. Report concise progress in commentary, inspect the complete log, correct the failure within the governing step, wait or poll as needed, and continue.
- A genuinely required human-assisted GUI or in-simulator observation is the only normal reason to pause before completion. When that occurs, follow the Human-Assisted Steps section exactly and resume the same workflow after confirmation; do not mark the package complete while the human gate is pending.

## Conversion Workflow

1. Inventory and hash all source files. Never delete, rename, move, or overwrite source files.
2. Create an output root with `scenery`, `texture`, `work`, and `logs`. Put backups and intermediate files only below `work`.
3. Classify every BGL before conversion as object/placement, airport, terrain/CVX, or legacy ground polygon. Record the decision for every file.
4. Recover and verify the complete airport definition before compiling general objects. Treat NewBglAnalyze output as provisional; compare counts for runway, starts, taxi points/paths, parking, aprons, communications, approaches, ILS, and navaids. Require ADE XML immediately when expected content is absent.
5. Finalize and prevalidate the complete airport XML before final BGLComp assembly. Confirm the ICAO, runway geometry, airport elevation, magnetic variation, AI graph mutations, hold-short geometry, `DeleteAirport` flags, and COM records are already final; correct only demonstrably invalid values. Then compile the airport BGL with FS2004 BGLComp; if a necessary correction requires recompilation, follow the retry discipline above and revalidate affected airport gates. Do not use BGLComp to discover XML/schema errors.
6. Audit elevation before object conversion. Compare airport elevation, flatten elevation, and every placement's AGL/MSL mode. Recreate a conservative FS2004 flatten when the FSX CVX flatten cannot be compiled; do not wait for buried or floating buildings to appear in FS2004.
7. Inventory texture stems case-insensitively and fail on collisions. Extract model material references, verify every referenced day/night texture has a unique output target, and preserve stems exactly.
8. Convert every DDS to vertically flipped, maximum 1024-pixel, DXT1/DXT3 extended BMP with a complete mip chain. Verify headers, dimensions, alpha mode, mip payload, and `_LM` pairing before model installation.
9. Configure MCX with `scripts/configure_mcx.py`. Expect repeated MCX license/permission dialogs; automate only those dialogs. If automation fails, pause and guide the user to click the agreement buttons.
10. Begin object conversion with explicit paths, but do not invoke BGLComp or create a provisional BGL_9 package. Export the source material record and latest DAE, compile provisional scenery `MDL_9` files with MakeMDL when target-format evidence is required, and immediately perform the whole-model `One/Zero` detection and correction in [references/onezero-materials.md](references/onezero-materials.md) during this same first-conversion pass. Match by model path and diffuse texture, correct every affected whole model, and reverse-export the corrected MDL. Keep only finalized MDLs for later final BGL_9 assembly; never copy a failed FSX-only BGL into final output, and never defer initial `One/Zero` detection to a later material audit or user-reported visual problem.
11. Rebuild missing object placements before simulator testing. Extract placement records from FSX placement BGLs, map their raw GUID bytes to the finalized FS2004 model GUIDs, and prepare separate airport and city placement XML. Prevalidate every placement but do not invoke BGLComp yet; placement BGL assembly is deferred until step 17 so later geometry/GUID decisions cannot force a second compile. Do not assume a converted library model is enough: a visible object needs both a finalized model and a valid FS2004 placement record.
12. Resolve user-reported objects by evidence, not names. When the user identifies an object by visual description, runway end, city side, direction, or relative position, parse placement XML/BGL coordinates, compute distance/bearing from known airport/runway landmarks, match placement GUIDs to model libraries, and only then edit or disable the confirmed placement or library. Do not infer the target from filename, texture name, or a visually similar model name alone.
13. Preserve FSX placement orientation exactly. Convert FSX placement heading/pitch/bank units into BGLComp degrees, keep `altitudeIsAgl` semantics, preserve scale, and validate representative airport and city objects against their source coordinates. If a batch of buildings is rotated or displaced, fix the placement conversion math before editing individual models.
14. Audit model-local geometry offsets before installing any single-model BGL placed at, or very near, the airport reference point. Export it to DAE, calculate the position-only bounding box and center, and transform that center through the placement heading into a geodetic location. Treat a center hundreds of metres from the model origin as suspicious and a kilometre-scale offset as a mandatory failure. Recenter every position array by the same local offset, preserve UVs/materials/animations, compile a new library GUID, and place it at the transformed center with the original heading and correct AGL/MSL semantics. Do not merely move the original far-from-origin placement: that applies the offset twice or leaves FS2004 precision/culling errors. Audit adjacent reference-point BGLs as a group because roads, fences, and buildings are often authored as separate but co-offset models.
15. Audit converted building libraries for material fidelity before installation. Export representative building BGLs to DAE/OBJ or MCX-readable reports, compare texture/material names with the FSX source, keep source stems and `_LM` pairings, and reject conversions whose materials become transparent, reordered, renamed, or assigned to the wrong surface. Recompile from the latest geometry-corrected DAE, after recentering, rotation, and other accepted model fixes; never fall back to stale source geometry that can undo those fixes or reintroduce placement errors.
16. Classify alpha by source material intent, not by DDS pixels alone. For every texture with alpha below 255, map it to its exact material and surface, inspect the source material's transparency/alpha-test flags, and classify it as intentional cutout/glass or non-transparency data. Never automatically choose transparent FS2004 rendering merely because a DDS contains alpha. If an opaque wall, roof, hangar, or sign texture contains zero alpha, create a model-specific opaque day/night copy or rebuild the material as opaque; do not overwrite a shared texture used by genuine cutouts. After compilation, audit the final DXT payload for actual transparent pixels and compare source/final material-to-texture bindings.
17. Before final library installation, verify that every converted library has a complete first-conversion `One/Zero` record from step 10. This is a consistency and regression gate, not the point of initial detection. Re-run MDL-only comparison for models rebuilt after step 10 by origin, rotation, placement, alpha-intent, or other accepted corrections, using the latest accepted DAE. Finalize all target MDLs, GUID mappings, and placement XML first. Only after they pass, assemble each model-library BGL and each placement BGL with BGLComp. Necessary correction/recompilation is allowed under the retry discipline above. Do not create routine provisional BGL probes or substitute a late post-conversion spot check for the step-10 MDL review.
18. Export legacy ground polygons to SCA, rewrite embedded `.dds` references to `.bmp`, and compile with SCASM. Confirm final material references resolve to the converted BMP set.
19. Set ground-polygon visibility deliberately. Use 20,000 m as the tested starting value when the source export contains `v1=10000`; apply it consistently to all airport ground-polygon SCA files.
20. Proactively inspect large or nearly flat object BGLs as DAE before final installation. Classify true ground-detail models separately from buildings, but do not assume this removes FS2004 shadow artifacts.
21. Perform a read-only final audit of AI departure and ATC behavior before simulator acceptance. Verify that the compiled result matches the pre-BGLComp graph approved in step 5: continuous parking-to-runway taxi graphs, matching runway-path numbers/designators, and every departure `HOLD_SHORT` node's orientation, runway-side topology, and perpendicular centerline distance. Treat about 225 ft / 68.6 m as the FS2004 maximum and target about 60 m. All node promotion/movement and old-hold demotion must already have occurred in step 5 before airport compilation. Keep this audit read-only; if it demonstrates a defect, return to the governing airport correction/build step, recompile as necessary, and repeat affected audits.
22. Perform a read-only verification of the compiled airport's `APPROACH`, `ATIS`, `GROUND`, and `TOWER` records, frequency-deletion semantics, and active-AFCAD priority against the step-5 precompile record. Keep verification read-only; a demonstrated defect may be corrected and recompiled in the governing airport build step, followed by renewed verification. Do not infer a runway mismatch from radio traffic alone; first exclude an overlapping frequency from another airport. Do not stack a COM-only overlay when its subrecords are byte-identical to those already embedded in the active airport BGL.
23. Run `scripts/validate_package.py` and complete every required build-time gate below before asking the user to test FS2004.

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
- **AI departure graph:** require every intended departure parking route to reach a continuous, correctly numbered runway path through a valid hold-short transition. Require all operational departure hold-short nodes to remain within about 68.6 m of the runway centerline, preferably about 60 m, with correct orientation and no path crossings or reversed node order.
- **ATC and radio:** verify `Com` record types/frequencies and `DeleteAirport` frequency flags in the final active BGL. Distinguish AI proximity-triggered handoff from player COM1 tuning, which must work away from the runway; use `.FLT` fields such as `Comm1Active`, `ATC_Agent`, `AgentTracking`, and `AgentHandoff` only as diagnostic evidence, not as conversion input.
- **Elevation:** install an FS2004-compatible flatten at the confirmed elevation and audit AGL/MSL placement semantics.
- **Texture availability:** ensure every final model/ground texture reference resolves case-insensitively to exactly one BMP.
- **Texture orientation:** flip all source DDS files during conversion and inspect representative text-bearing textures before packaging.
- **Material integrity:** compare source/exported material names and day/night pairs; do not rename, merge, or deduplicate unrelated textures.
- **Building completeness:** for every source building/terminal/object library and placement BGL, record whether the final package contains a matching FS2004 library BGL and a compiled placement BGL. Treat missing terminal/city buildings as a build failure unless the skip is explicit and documented.
- **Building material fidelity:** inspect representative terminal, cargo, hotel, city, and vegetation/cutout models for wrong transparency, wrong face texture assignment, missing `_LM`, and upside-down text. Fix material conversion and texture preparation before accepting the package.
- **Opaque render queue:** perform the source-versus-first-build comparison during step 10 for every model/texture pair, not as an end-of-run discovery task. A source `1.0` material that becomes about `0.988235` with `SrcAlpha/InvSrcAlpha` is a mandatory first-conversion failure. Rebuild every textured material in each affected whole model as `One/Zero`, then require zero remaining blended textured materials in its reverse export. Later rebuilds receive regression verification in step 17. Preserve the latest corrected geometry, GUID, placement, final BMP files, and all non-target MDLs.
- **Model-origin locality:** inspect every single-model BGL placed at the airport reference point and every model with a bounding-box center far from `(0,0)`. Require recentering plus geodetic re-placement for suspicious offsets, then verify the final geometry footprint rather than only the placement record.
- **Alpha intent:** inventory every source texture containing non-opaque alpha and record its referencing material, source transparency flags, surface purpose, selected FS2004 format, and final transparent-pixel count. Opaque architectural materials must finish with zero transparent pixels; intentional fence/vegetation/glass cutouts must retain their alpha. DXT1/DXT3 selection alone is not proof.
- **Placement orientation and position:** compare source and final lat/lon/alt/heading/pitch/bank/scale for sampled airport and city objects. Treat global rotation, mirrored heading, or systematic offset as a conversion bug in placement decoding, not as a manual per-building adjustment.
- **Object targeting evidence:** for any user-reported object or direction-specific issue, document the parsed coordinates, distance/bearing to a known landmark, placement GUID, matched model library, and exact BGL/XML record before changing it. Filename or texture-name similarity alone is not enough evidence.
- **Ground format:** rewrite all embedded ground `.dds` references, compile with SCASM, and verify final BGLs contain no `.dds` strings.
- **Mipmaps and distance:** verify complete mip chains independently from SCA `v1` visibility; prioritize single-mip BMPs, mip declaration/payload inconsistencies, and heavy model UV repetition, using unusual dimensions only as supporting evidence; use 20 km unless the user requests another tested value.
- **Package integrity:** require unchanged source hashes, nonempty structurally valid BGLs with the expected model/placement/facility content, valid extended BMP headers, documented skips, and a clean latest successful compiler log for every installed BGLComp output. Preserve all earlier attempts, including failures, in the invocation manifest with reasons for retries. Multiple invocations are not a validation failure when necessary corrections and revalidation are documented; missing attempt records, unexplained retries, a latest error log, or an empty-header output fail validation.

## Human-Assisted Steps

When a GUI step is genuinely needed, stop automation, explain why, give numbered instructions in the user's language, state the exact output path/filename to create, and state how completion will be verified. This is the only normal workflow pause: do not end the session for non-human work. Continue only after the user confirms completion or the expected file appears, then resume the remaining numbered steps without asking for a separate “continue” instruction.

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
- Accept a package only when validation reports `valid: true`, source hashes are unchanged, BGLs are nonempty, BMP headers are FS2004-compatible, no final BGL references `.dds`, and the airport passes an in-simulator smoke test. Start a new flight rather than loading a `.FLT` with serialized ATC state; with a default aircraft, confirm COM1 can select ATIS and Tower away from the runway, then observe representative AI through parking, taxi, hold-short, Tower contact, runway entry, and takeoff roll from both runway ends or every operational departure entrance.

## Bundled Scripts

- `scripts/configure_mcx.py`: configure FS2004 compiler paths for MCX.
- `scripts/convert_scenery.py`: perform guarded texture work and final BGL conversion; do not use its BGL output mode before the final assembly in step 17.
- `scripts/inspect_bgl.py`: export BGLs and optionally capture transient placement XML.
- `scripts/rewrite_sca_textures.py`: change SCA texture references from DDS to BMP.
- `scripts/adjust_sca_visibility.py`: safely change expected `RefPoint` visibility values.
- `scripts/validate_package.py`: validate source integrity and final package formats.
