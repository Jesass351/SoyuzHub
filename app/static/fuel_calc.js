
function calcFuel(){
    let duration = parseInt(document.getElementById("duration").value);
    let consumption = parseFloat(document.getElementById("consumption").value);
    let lapTimeMin = parseInt(document.getElementById("lapTimeMin").value);
    let lapTimeSec = parseInt(document.getElementById("lapTimeSec").value);
    let isZeroLap = document.getElementById("isZeroLap").checked;

    let lapCount = Math.ceil(duration * 60 / (lapTimeMin * 60 + lapTimeSec));
    let lapsFuel = lapCount * consumption;

    if (isNaN(lapCount)) { lapCount = 0}
    if (isNaN(lapsFuel)) { lapsFuel = 0}
    if (isNaN(consumption)) { consumption = 0}
    if (isNaN(lapTimeMin)) { lapTimeMin = 0}
    if (isNaN(lapTimeMin)) { lapTimeMin = 0}

    document.getElementById("totalFuel").textContent = duration;
    document.getElementById("lapCount").textContent = lapCount;

    if (isZeroLap){
        let zeroLapFuel = consumption * 1.8;
        let totalFuel = lapsFuel + zeroLapFuel;

        document.getElementById("totalFuel").textContent = Math.ceil(totalFuel);
        document.getElementById("zeroLapFuel").textContent = Math.ceil(zeroLapFuel);
        document.getElementById('zeroLapFuelP').classList.remove('d-none');
    } else {
        document.getElementById("totalFuel").textContent = Math.ceil(lapsFuel);
        document.getElementById('zeroLapFuelP').classList.add('d-none');
    }
}

window.addEventListener("load", () => {
    document.getElementById("duration").onchange = calcFuel;
    document.getElementById("consumption").onchange = calcFuel;
    document.getElementById("lapTimeMin").onchange = calcFuel;
    document.getElementById("lapTimeSec").onchange = calcFuel;
    document.getElementById("isZeroLap").onchange = calcFuel;


  })