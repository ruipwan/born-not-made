/* Time samples in the archived FE export are rounded individually.
   Both the 3D replay and the reference plot use the stored time axis. */
const BirthTrace = (() => {
  function interval(times, time) {
    let left = 0;
    let right = times.length - 1;
    if (time <= times[left]) return {left, right: left, fraction: 0};
    if (time >= times[right]) return {left: right, right, fraction: 0};
    while (right - left > 1) {
      const middle = Math.floor((left + right) / 2);
      if (times[middle] <= time) left = middle;
      else right = middle;
    }
    return {left, right, fraction: (time - times[left]) / (times[right] - times[left])};
  }
  function at(times, values, time) {
    const {left, right, fraction} = interval(times, time);
    return values[left] + (values[right] - values[left]) * fraction;
  }
  return {interval, at};
})();
