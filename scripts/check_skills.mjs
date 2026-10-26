// MIT: original packaging tooling. The hash protocol matches skills 1.7.2.
import { createHash } from "node:crypto";
import { readdir, readFile } from "node:fs/promises";
import { dirname, join, relative, resolve } from "node:path";
import { fileURLToPath } from "node:url";

export async function skillFolderHash(directory) {
  const files = [];
  async function collect(current) {
    for (const entry of await readdir(current, { withFileTypes: true })) {
      if (entry.isSymbolicLink()) throw new Error(`Symlink in managed skill: ${entry.name}`);
      const path = join(current, entry.name);
      if (entry.isDirectory()) {
        if (entry.name !== ".git" && entry.name !== "node_modules") await collect(path);
      } else if (entry.isFile()) {
        files.push({ path: relative(directory, path).replaceAll("\\", "/"), data: await readFile(path) });
      }
    }
  }
  await collect(directory);
  files.sort((a, b) => a.path.localeCompare(b.path));
  const hash = createHash("sha256");
  for (const file of files) hash.update(file.path).update(file.data);
  return hash.digest("hex");
}

export async function checkManagedSkills(root) {
  const lock = JSON.parse(await readFile(join(root, "skills-lock.json"), "utf8"));
  if (lock.version !== 1) throw new Error("Unsupported skills lock version");
  for (const [name, entry] of Object.entries(lock.skills)) {
    if (!/^[a-z0-9][a-z0-9-]*$/.test(name)) throw new Error(`Unsafe skill name: ${name}`);
    const actual = await skillFolderHash(join(root, ".agents", "skills", name));
    if (actual !== entry.computedHash) throw new Error(`Managed skill hash mismatch: ${name}`);
  }
  return Object.keys(lock.skills).length;
}

if (import.meta.main) {
  const root = resolve(dirname(fileURLToPath(import.meta.url)), "..");
  try {
    console.log(`PASS: ${await checkManagedSkills(root)} managed skill content hashes match the CLI-generated lock`);
  } catch (error) {
    console.error(`ERROR: ${error.message}`);
    process.exitCode = 1;
  }
}
