// TiffyAI GitHub-hosted wallet setup (focus: Miner app first)

import { createWeb3Wallet } from '@reown/walletkit';
import { Core } from '@walletconnect/core';
import { buildApprovedNamespaces } from '@walletconnect/utils';

const core = new Core({
  projectId: 'bf40c7dcdb05f06f2769573103007576' // Replace this with your WalletConnect project ID from cloud.walletconnect.com
});

async function setupWallet() {
  try {
    const wallet = await createWeb3Wallet({
      core,
      metadata: {
        name: "TiffyAI Miner",
        description: "Mine and upgrade using your wallet",
        url: "https://tiffyai.github.io", // use the verified GitHub domain
        icons: ["https://tiffyai.github.io/logo.png"] // change this if you have another icon
      }
    });

    window.tiffyWallet = wallet;
    console.log("✅ Wallet initialized successfully");

    // Example event: Log connections
    wallet.engine.signClient.on('session_proposal', (proposal) => {
      console.log("📡 WalletConnect session proposal:", proposal);
    });
  } catch (err) {
    console.error("❌ Wallet initialization failed:", err);
  }
}

setupWallet();
