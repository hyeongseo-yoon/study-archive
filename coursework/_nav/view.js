// 노트 상단 네비게이션: 같은 과목의 notes / class-note 목차, 짝 노트, 이전/다음
const cur = dv.current().file.path;
const m = cur.match(/^(.*)\/(notes|class-note)\/([^/]+)\.md$/);
if (m) {
    const [, course, kind, name] = m;
    const nat = (a, b) => a.localeCompare(b, undefined, { numeric: true });
    const list = (k) => app.vault.getMarkdownFiles()
        .filter(f => f.path.startsWith(`${course}/${k}/`) && f.parent.path === `${course}/${k}`)
        .filter(f => f.path !== `${course}/${k}/공부 계획.md`)
        .sort((a, b) => nat(a.basename, b.basename));
    const label = (f) => {
        const t = f.basename.match(/^(?:chapter|lecture)-([\d-]+?)(?:-[a-z].*)?$/);
        return t ? t[1] : f.basename;
    };
    const link = (f, alias) => `[[${f.path.replace(/\.md$/, "")}|${alias ?? label(f)}]]`;
    const row = (files) => files.map(f => f.path === cur ? `**${label(f)}**` : link(f)).join(" · ");
    const notes = list("notes"), cls = list("class-note");
    const files = kind === "notes" ? notes : cls;
    const i = files.findIndex(f => f.path === cur);
    const courseName = course.split("/").pop();
    const lines = [`📚 **${courseName}** — ${kind === "notes" ? "정리노트" : "수업노트"}`, `목차: ${row(notes)}`];
    if (kind === "class-note") lines.push(`수업노트: ${row(cls)}`);
    const pair = (kind === "notes" ? cls : notes).find(f => f.basename === name);
    if (pair) lines.push(`${kind === "notes" ? "수업노트" : "정리노트"}: ${link(pair, "이 챕터")}`);
    const pn = [];
    if (i > 0) pn.push(`◀ ${link(files[i - 1], "이전")}`);
    if (i >= 0 && i < files.length - 1) pn.push(`${link(files[i + 1], "다음")} ▶`);
    if (pn.length) lines.push(pn.join(" | "));
    dv.paragraph(lines.join("\n\n"));
}
