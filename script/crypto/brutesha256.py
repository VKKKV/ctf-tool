from hashlib import sha256

dic = "/home/kita/ctf/tool/dict/rockyou.txt"

# const salt = "3NL/usjb4vEg";
# const hash =
# "9bcf0c8289a97d33021b4790659396d9f8af1085210d2186b8ec38efcdc31472";
#
# window.onload = () => {
# document.getElementById("challenge_form").onsubmit = (e) => {
#   const value = document.getElementById("challenge_answer").value;
#   if (sha256(salt + value).hex() !== hash) {
#     alert("Wrong password.");
#     e.preventDefault();
#     return false;
#   }
# };
# };


while True:
    with open(dic) as f:
        for line in f:
            s = "3NL/usjb4vEg" + line.strip()
            if (
                sha256(s.encode()).hexdigest()
                == "9bcf0c8289a97d33021b4790659396d9f8af1085210d2186b8ec38efcdc31472"
            ):
                print(line.strip())
                break
