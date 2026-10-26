import { afterEach, expect, test } from "bun:test";
import { createHash } from "node:crypto";
import { cp, mkdir, mkdtemp, rm, symlink, writeFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { checkManagedSkills, skillFolderHash } from "../scripts/check_skills.mjs";

const root = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const temporary = [];
afterEach(async () => { for (const dir of temporary.splice(0)) await rm(dir, { recursive: true, force: true }); });
async function fixture() {
  const dir = await mkdtemp(join(tmpdir(), "odm-skills-"));
  temporary.push(dir);
  return dir;
}

test("committed copies match actual manager hashes", async () => {
  expect(await checkManagedSkills(root)).toBe(3);
});

test("edited managed content is rejected", async () => {
  const dir = await fixture();
  await cp(join(root, ".agents"), join(dir, ".agents"), { recursive: true });
  await cp(join(root, "skills-lock.json"), join(dir, "skills-lock.json"));
  await writeFile(join(dir, ".agents/skills/refactor/SKILL.md"), "changed after install");
  await expect(checkManagedSkills(dir)).rejects.toThrow("hash mismatch: refactor");
});

test("hash includes paths and bytes in JavaScript localeCompare order", async () => {
  const dir = await fixture();
  const names = ["SKILL.md", "a_b.md", "a-b.md", "a.md"];
  await mkdir(join(dir, "nested"));
  for (const name of names) await writeFile(join(dir, "nested", name), name);
  const expected = createHash("sha256");
  for (const path of names.map(n => `nested/${n}`).sort((a, b) => a.localeCompare(b))) {
    expected.update(path).update(path.slice("nested/".length));
  }
  expect(await skillFolderHash(dir)).toBe(expected.digest("hex"));
});

test("symlinks cannot escape a managed skill", async () => {
  const dir = await fixture();
  await symlink(join(root, "README.md"), join(dir, "outside.md"));
  await expect(skillFolderHash(dir)).rejects.toThrow("Symlink in managed skill");
});
