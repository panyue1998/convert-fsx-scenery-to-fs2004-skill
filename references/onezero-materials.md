# Default Whole-Model One/Zero Correction

Use this during the first conversion pass for every FSX model, before any BGLComp invocation. Initial detection and correction operate on provisional FS2004 scenery MDLs made with MakeMDL, never on a provisionally assembled BGL. If later model-origin, rotation, placement, or alpha-intent work changes a model, repeat the MDL-only comparison as regression verification against the latest accepted DAE. Assemble the final model-library BGL only after every target MDL and GUID decision is final. This prevents daytime building/building and cloud/building depth-order faults caused by nearly opaque architecture entering FS2004's transparent render queue while keeping material probes at MDL level and auditing necessary final rebuilds.

## Timing And Final Assembly

1. Extract the source material record and prepare the latest DAE before packaging any library BGL.
2. Compile a provisional FS2004 scenery `MDL_9` with MakeMDL and reverse-export that MDL for material comparison. This provisional MDL may be rebuilt as needed; it must not be wrapped in XML or passed to BGLComp.
3. Complete the whole-model correction and all regression checks at MDL level. Finalize model GUIDs and placement XML only after the accepted MDLs are known.
4. Assemble final library and placement BGLs only after MDL/material/GUID/placement gates pass. Necessary correction/recompilation is allowed under the SKILL.md retry discipline without a separate approval solely for recompilation. Preserve every attempt and its reason; require the latest installed result to have a clean log and validated content. Do not routinely use BGLComp for syntax or material probes.

## Detection

1. Export the FSX source models and the first provisional FS2004 MDL build to X or another report that exposes base material alpha and blend factors. Do this immediately during the model's first conversion pass and before BGLComp is called.
2. Match records by case-insensitive relative model path and diffuse texture name. Do not match by material index alone because conversion can reorder materials.
3. Mark a model affected when at least one matched textured material has all of these properties:
   - source base alpha is `1.0`;
   - reverse-exported FS2004 base alpha is approximately `0.988235`;
   - reverse-exported blend factors are `SrcAlpha/InvSrcAlpha`.
4. Record the affected model list, matched model/texture pairs, and owning library. Scan every converted library rather than only visually reported buildings.

## Correction

1. Use the latest accepted DAE for each affected model. It must already include recentering, local-axis rotation, ferris-wheel or other special geometry corrections, and any corresponding placement decision. Never rebuild from stale FSX X/DAE geometry after those fixes.
2. Create a compile-only staging directory. Copy the DAE and its referenced PNG inputs there, forcing the staging PNG alpha to `255` so MCX/MakeMDL emits opaque `One/Zero` materials.
3. Compile the complete affected model as FS2004 scenery MDL. Change every textured material in that model to `One/Zero`, not only the originally matched material. FS2004 can place the whole model or a broad model batch in its transparent queue when any nearly opaque architectural material remains blended.
4. Do not install the compile-only opaque PNG files. Keep the already converted final BMP day and `_LM` textures byte-for-byte unchanged; the staged PNG alpha is only a compiler hint for the MDL render state.
5. Keep the finalized library GUID and placement XML. Build the owning library with corrected target MDLs; recompile when a necessary accepted correction requires it, while copying every non-target MDL from the latest accepted MDL baseline byte-for-byte. This preserves unrelated fixes without creating a provisional BGL.

## Verification Gates

- Reverse-export every corrected provisional MDL before BGLComp and require every textured material to use `One/Zero`; any remaining `SrcAlpha/InvSrcAlpha` material is a build failure.
- Require identical face counts and model-space bounds before and after correction. MakeMDL may split or merge a few duplicate vertices when material batches change; record this but accept it only when face counts and all bounds remain equal within `0.01 m`.
- Explicitly compare special corrected models, such as a rotated wheel, against their post-fix geometry rather than the original conversion.
- Require the finalized GUID mapping, finalized placements, unchanged final BMP hashes, byte-identical non-target MDLs, no final `.dds` reference, and complete records of every BGLComp attempt, a clean latest successful build, and renewed verification after necessary recompilation.
- Archive only the package-local `SCENERY.dat`, restart FS2004 completely, and test daytime building/building and cloud/building order plus night lighting.

Run the applicable [geometry, alpha and alignment gates](geometry-texture-audits.md) after a split, projection or component-grouping repair. `One/Zero` checks do not establish UV lineage or component placement. Compile-only opaque PNG hints remain separate from final BMP alpha, especially invisible seasonal layers.

## Proven Non-Fixes

- Making final BMP files opaque does not change an MDL that remains in the transparent render queue.
- Correcting only one facade or a few triangles may not change model-level scheduling.
- Rebuilding from stale source geometry can undo recentering or rotation and cause widespread placement errors.
