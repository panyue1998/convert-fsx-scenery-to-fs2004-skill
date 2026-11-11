# Geometry, Alpha, And Component Alignment Audits

Apply these checks inside workflow steps 6, 8, 10, 14, 16–18 and the final build-time gates. They do not authorize changes to other scenery packages or simulator global folders.

## Ground curvature and height

- Classify coordinates as well as the BGL container. A legacy/SCASM BGL can load in FS2004 while still containing FSX-curved ground. A compatible header is not proof of compatible geometry.
- Decode reference coordinates, local units/scale, AGL/MSL mode, vertex heights, layer calls and flatten coverage. Check the entire footprint, including edges. Negative heights alone are not proof of a defect: they may describe intended terrain or real 3D geometry.
- FSX curvature can put distant vertices of nominal ground below an FS2004 flatten. In Helsinki, fitted curvature accounted for vertices down to about -0.8894 m; close views exposed the base airport surface. Restoring the confirmed ground plane while preserving layers resolved this in the simulator. Visibility and mipmaps were separate issues.
- Remove curvature only from confirmed ground, or use a verified geocentric-to-target-flat conversion. Preserve intended layer ordering, small ground offsets, geographic footprint, UVs and seasonal/day/night branches. Helsinki's 0.01 m offset is a case value, not a universal setting. Never flatten buildings, slopes or vertical light billboards with a blanket Y/Z assignment.
- Distinguish the first-loaded airport datum, hard/flatten surface and visible ground polygons. In Helsinki, the default EFHK datum was 50.901 m while the converted airport used 54.558 m. A separately authorized early-load altitude-only BGL corrected the datum; it did not replace the curvature repair. Inspect actual airport records and scenery order first. Do not overwrite default airports or install global-folder overrides without authorization for that exact external change.
- When preserving conditional native code requires a narrow binary repair, back up the active output and allowlist decoded vertex fields. Require unchanged structure and every other byte, including UVs, references, branches and layers. Verify the actual layout and scale; do not copy offsets from another BGL blindly.

## Texture alpha and orientation

Inventory existing BMPs as well as DDS files.

1. Inspect raw BGRA bytes in simulator textures stored as 32-bit `BI_RGB` BMP. Generic readers, including Pillow's normal BMP path, can discard the fourth byte and report alpha 255. Ordinary RGBX BMPs can also have zero padding, so establish meaningful alpha from material intent and asset purpose before treating that byte as transparency.
2. Decode meaningful alpha explicitly with correct row stride and top-down/bottom-up origin. Record source alpha-0, alpha-1..254 and alpha-255 counts. Do not use the decoder that lost alpha as the sole validator.
3. Preserve intentionally invisible seasonal placeholders. Helsinki's `winter.bmp`, `winter_sp.bmp` and `winter_fa.bmp` were 4×4 white RGB images with alpha 0. Converting them to opaque white caused taxiway/apron-shaped overlays despite complete texture references. Hiding AFCAD apron surfaces did not solve this defect. Distinguish missing files, lost alpha and visible airport overlays before changing airport geometry or parking widths.
4. Check the encoder too: in this toolchain, ImageTool treated entirely zero-alpha TGA input as if alpha were absent, even with DXT3 selected. Validate final compressed alpha pixels, FS70 alpha metadata and mip payload; an intermediate RGBA histogram or format name is insufficient.
5. If verified all-zero alpha is lost, use an alpha-preserving encoder or repair the known DXT3 alpha blocks and matching metadata in staging. Helsinki's exact FS70 layout used metadata `0x400` and zero DXT3 alpha nibbles. This is an observed layout, not a value to write into arbitrary BMPs. Independently decode the payload and reverse-export with native ImageTool before installation.
6. Preserve genuine glass/cutouts/sprites, and handle opaque material-data alpha separately under step 16. Compile-only opaque PNG hints for `One/Zero` must never replace final transparent BMPs.
7. Verify orientation through native reverse export and readable text. A DDS-wrapper decoder for compressed extended BMP may need an explicit row flip; do not compensate by guessing UV flips. Respect ImageTool's actual rectangular mip layout instead of appending guessed 1-by-N tails to satisfy a generic full-chain rule.

## Immutable shared-index splitting

COLLADA `VERTEX`, `NORMAL` and `TEXCOORD` inputs can share the **same index offset** while referencing different arrays. Remapping a column for positions and then selecting normals/UVs from the already-remapped column silently corrupts those attributes. Bounds and position-only checks can still pass.

For each face-range split:

1. Keep an immutable original primitive-index slice.
2. Compute `used` and `inverse` once per unique **offset**, from that immutable slice.
3. Select every source array associated with an offset using the same original `used` rows. Write compacted index columns only after mappings are frozen.
4. For example, original `(5, 9, 10)` may become `(0, 1, 2)`, but position, normal and UV arrays must all select original rows `(5, 9, 10)`. Normals/UVs must not select original rows `(0, 1, 2)` because positions were processed first.
5. Compose mappings back to original arrays when splitting again. Preserve material bindings, seams, node transforms, UV sets and triangle winding.

Before final BGLComp assembly, reverse-export each split MDL and verify **joint position + UV + material correspondence** through the accepted coordinate transforms, plus normal directions in the correct frame. Coincident positions can legitimately have different UVs at seams. Account explicitly for exporter V-origin changes and compiler welding. Use documented tolerances: Helsinki used about 1 cm for positions and 0.0001 for UVs; actual UV errors were much smaller.

Check a splitter with nonzero, non-contiguous shared indices and multiple split stages. Require triangle-corner attribute correspondence and coverage, not just equal array lengths, bounds or a texture-atlas screenshot.

Budget for double-sided expansion and position/normal/UV seam duplication before MakeMDL. The observed toolchain could silently lose faces after an index budget was exceeded while returning success. Validate compiled coverage and non-thin triangles; record accepted sub-centimetre welding loss separately.

## Coordinate frames and component coherence

Geographic fidelity and alignment in the **target renderer's coordinates** are separate checks. A WGS84/ECEF round-trip alone does not prove independently referenced parts line up in FS2004.

- Mark source/current artifacts as already-flat legacy geometry, FSX-relative geocentric geometry or another verified convention. Preserve the latest accepted geometry/material fixes. Do not globally reproject original native 3D fixtures merely because they share a directory with curved ground.
- Verify axes, units, heading, AGL/MSL heights and references. Convert through the correct source frame to geographic position and then the target flat frame. Transform normals with the appropriate inverse-transpose/Jacobian; preserve UVs, materials and animation relationships. Do not remove curvature twice.
- The installed MCX `ASToFra.Coordinates` implementation in this case used:

  ```text
  E = R_E * cos(phi0) * (lambda - lambda0)
  N = R_N * (phi - phi0)
  R_E = 6378134.344407706 m
  R_N = 6367311.808277457 m
  ```

  Angles are radians. These are flat-map parameters, not WGS84 ellipsoid radii for ECEF. Verify the installed tool/target convention and independent coordinate samples before reuse. MCX coordinate vectors use longitude, latitude, altitude; its flat helper returns altitude as Z, so handle reference-relative/AGL height explicitly rather than subtracting altitude twice.
- Invert the **target flat mapping** to verify geographic fidelity, then compare source-coincident seams across different parts in a common target frame. Match halos to the correct marking/fixture; a nearest unrelated fixture, billboard bounding-box centre or complete texture inventory does not identify the intended luminous position.
- Partition by complete physical object or coherent local group before material/face budgets. Keep a bus's shell, chassis, wheels and seats in one MDL/reference when feasible. If limits require several parts, use a shared local frame/reference and verify relative transforms. Apply this to glass/structure and lamp/glow pairs while respecting locality and compiled-index budgets for large objects.
- Helsinki's 26 complete-bus models were confirmed aligned by the user. Replacing 3 airport-wide fragments required new GUIDs and a placement rebuild; the other 91 placement records remained byte-identical. Repartitioning does not authorize moving unrelated objects.
- The later glass/ground-light projection repair passed build-time checks. A diagnostic common-plane estimate reduced maximum terminal coincident-point gaps from about 1.16 m to 0.032 m, and landside from about 0.32 m to 0.011 m. **The user subsequently confirmed that the glass and light alignment correction was correct in FS2004.** The quoted gaps remain build-time numeric estimates, not in-game measurements. Reuse the verified method and audit gates, not case-specific offsets or an unverified projection constant.

## Evidence and acceptance

Record source/current coordinate conventions, BGL record/native reference, GUID, target placement, original-to-final attribute lineage, alpha counts, compiled XYZ/UV/material results and every necessary compiler attempt. Verify model/placement content; where the SDK embeds MDLs unchanged, compare full payload bytes as well as GUIDs.

Use backups and byte/record allowlists to show accepted objects, non-target placements, textures, airport records and native seasonal code survived. Synchronize canonical XML/DAE/model manifests and current audit counts; retain earlier artifacts as history instead of leaving stale inputs that can undo a fix.

Require a complete restart and new flight for runtime acceptance. Inspect close/low ground views, invisible seasonal overlays, vehicle body/interior alignment, glass seams and dusk/night lights. Keep build-time checks and user-confirmed runtime results distinct.

Background: [FS2004 flat versus FSX geocentric coordinates](https://www.fsdeveloper.com/wiki/index.php/Align_background_image_in_3D_editor), [MCX earth-curve discussion](https://www.scenerydesign.org/2012/07/correcting-for-the-fsx-curved-earth/).
