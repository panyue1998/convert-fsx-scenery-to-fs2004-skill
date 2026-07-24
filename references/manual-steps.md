# Manual Steps

## ADE: Recover Complete Airport XML

Use this when NewBglAnalyze output lacks expected airport facilities or ADE reports that a candidate BGL contains no airport.

Chinese guidance:

1. 在 ADE 中打开实际包含机场定义的 BGL；CVX 文件名不代表它一定只含地形数据。
2. 确认画面中能看到跑道、起点、滑行道节点与路径、停机位和停机坪。
3. 使用 ADE 的保存/导出 XML 功能，将完整 XML 保存到 `<output>\work\airport\<ICAO>_source.xml`。不同 ADE 版本的菜单可能显示为 `Save XML` 或 `Export XML`。
4. 不要覆盖原始 BGL，也不要只提交 ADE 工程文件。
5. 告知 Codex 文件已保存；Codex 应统计并报告关键 XML 元素后再编译。

English guidance:

1. Open the BGL that actually contains the airport definition in ADE; a CVX-like filename does not prove that it contains terrain only.
2. Confirm that runway, starts, taxi nodes/paths, parking, and aprons are visible.
3. Use ADE's Save XML or Export XML command and write the complete XML to `<output>\work\airport\<ICAO>_source.xml`.
4. Do not overwrite the source BGL and do not provide only an ADE project file.
5. Tell Codex that the file is ready; Codex must count key XML elements before compiling it.

Minimum plausibility checks depend on the airport, but an existing developed airport should not unexpectedly have zero `Runway`, `TaxiwayPoint`, `TaxiwayPath`, `TaxiwayParking`, or `Apron` elements. Compare analyzer and ADE outputs rather than trusting file size alone.

## MCX Permission Reminder

MCX may show the Usage License/Permission Reminder multiple times in one command. Automation may click only buttons owned by the MCX process and only when the window title identifies the license/reminder dialog. If it remains visible:

- Chinese: 依次点击协议窗口中的 `Next/下一步`、`Agree/同意` 或 `OK/确定`，不要操作其他程序的窗口；每次再次出现时重复。
- English: Click `Next`, `Agree`, or `OK` in the MCX license/reminder window only, repeating whenever it reappears.

## DXTBmp Inspection

Use DXTBmp only when a small number of textures still have orientation or alpha defects after batch conversion. Open the final BMP, inspect image orientation and alpha, save to a temporary file under `work`, then re-encode through FS2004 ImageTool with mipmaps. Preserve the original output texture as a backup.
