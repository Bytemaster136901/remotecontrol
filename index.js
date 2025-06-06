// UUIDs for your custom Bluetooth device (must match your receiver's GATT service/characteristics)
const SERVICE_UUID = '0000abcd-0000-1000-8000-00805f9b34fb'; // Example Service UUID
const CHARACTERISTIC_UUID = '0000dcba-0000-1000-8000-00805f9b34fb'; // Example Char UUID

let device, server, characteristic;

function displayBluetoothNeededMessage() {
  document.getElementById('status').textContent = 'To use this, bluetooth is needed';
  document.getElementById('remote').style.visibility = 'hidden';
}

function isBluetoothAvailable() {
  return navigator.bluetooth && typeof navigator.bluetooth.getAvailability === 'function';
}

async function checkBluetoothState() {
  if (!isBluetoothAvailable()) {
    displayBluetoothNeededMessage();
    return false;
  }
  const available = await navigator.bluetooth.getAvailability();
  if (!available) {
    displayBluetoothNeededMessage();
    return false;
  }
  return true;
}

async function connectBluetooth() {
  if (!(await checkBluetoothState())) return;
  try {
    device = await navigator.bluetooth.requestDevice({
      filters: [{ services: [SERVICE_UUID] }]
    });
    server = await device.gatt.connect();
    const service = await server.getPrimaryService(SERVICE_UUID);
    characteristic = await service.getCharacteristic(CHARACTERISTIC_UUID);
    document.getElementById('status').textContent = 'Connected to ' + device.name;
    document.getElementById('remote').style.visibility = 'visible';
  } catch (err) {
    document.getElementById('status').textContent = 'Connection failed: ' + err;
  }
}

async function sendCommand(cmd) {
  if (!characteristic) return;
  try {
    await characteristic.writeValue(new TextEncoder().encode(cmd));
  } catch (err) {
    document.getElementById('status').textContent = 'Send failed: ' + err;
  }
}

document.getElementById('connectBtn').onclick = connectBluetooth;

// Command mapping (sent to your receiver device)
const commands = {
  power: 'POWER_OFF',
  up: 'UP',
  down: 'DOWN',
  left: 'LEFT',
  right: 'RIGHT',
  ok: 'OK',
  home: 'HOME',
  back: 'BACK',
  menu: 'MENU',
  volup: 'VOL_UP',
  voldown: 'VOL_DOWN',
  mute: 'MUTE'
};

Object.keys(commands).forEach(key => {
  document.getElementById(key).onclick = () => sendCommand(commands[key]);
});

// Keyboard support: Arrow keys and Enter
document.addEventListener('keydown', (e) => {
  if (document.getElementById('remote').style.visibility !== 'visible') return;
  switch (e.key) {
    case 'ArrowUp':
      sendCommand('UP');
      break;
    case 'ArrowDown':
      sendCommand('DOWN');
      break;
    case 'ArrowLeft':
      sendCommand('LEFT');
      break;
    case 'ArrowRight':
      sendCommand('RIGHT');
      break;
    case 'Enter':
      sendCommand('OK');
      break;
    case 'Escape':
      sendCommand('BACK');
      break;
    case 'Home':
      sendCommand('HOME');
      break;
    case 'm':
      sendCommand('MENU');
      break;
    case 'v':
      sendCommand('VOL_UP');
      break;
    case 'c':
      sendCommand('VOL_DOWN');
      break;
    case 'u':
      sendCommand('MUTE');
      break;
    case 'p':
      sendCommand('POWER_OFF');
      break;
    default:
      break;
  }
});

// Initial Bluetooth check on page load
window.addEventListener('DOMContentLoaded', async () => {
  await checkBluetoothState();
  if (isBluetoothAvailable()) {
    navigator.bluetooth.addEventListener('availabilitychanged', (event) => {
      if (!event.value) {
        displayBluetoothNeededMessage();
      } else {
        document.getElementById('status').textContent = 'Bluetooth available. Click "Connect Bluetooth" to begin.';
      }
    });
  }
});