/* Shared by the assembly viewer and the print console. Positions in the Blender frame are metres. */
const MotherShell = {
  setRise(geometry, rest, riseMm) {
    const position = geometry.getAttribute("position");
    const rise = riseMm / 1000;
    for (let i = 0; i < rest.length; i += 3) {
      const x = (rest[i] + 0.015) / 0.29;
      const y = rest[i + 1] / 0.305;
      const z = rest[i + 2];
      const aboveSeam = Math.max(0, Math.min(1, (z - 0.02) / 0.10));
      const blend = aboveSeam * aboveSeam * (3 - 2 * aboveSeam);
      position.array[i + 2] = z + rise * Math.max(0, 1 - x*x - y*y) * blend;
    }
    position.needsUpdate = true;
    geometry.computeVertexNormals();
    geometry.computeBoundingSphere();
  }
};
