import { connectWallet } from './wallet.js';

document.getElementById('connectBtn').addEventListener('click', async () => {
  try {
    const address = await connectWallet();
    const short = address.slice(0, 6) + "..." + address.slice(-4);
    document.getElementById('connectBtn').innerText = `✅ ${short}`;
  } catch (err) {
    alert("❌ Wallet connection failed");
    console.error(err);
  }
});
