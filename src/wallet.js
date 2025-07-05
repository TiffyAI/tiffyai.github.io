// src/wallet.js
import { WalletKit } from '@reown/walletkit';

let wallet;
let signer;
let address;

export async function initWalletKit() {
  wallet = new WalletKit({
    chains: [56], // BNB Chain
    projectId: 'bf40c7dcdb05f06f2769573103007576', // Replace with your actual projectId from Reown
  });

  await wallet.init();
  return wallet;
}

export async function connectWallet() {
  if (!wallet) await initWalletKit();
  await wallet.connect();
  signer = wallet.getSigner();
  address = await signer.getAddress();
  return address;
}

export function getSigner() {
  return signer;
}

export function getWalletAddress() {
  return address;
}
