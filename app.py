import streamlit as st
import secrets
import time


class Ja1pr750:
    def __init__(self, key1, key2, key3, abeceda, supress="abcdefghijklmnop"):
        self.key1 = key1
        self.key2 = key2
        self.key3 = key3
        self.abeceda = abeceda
        self.supress = supress
        self.mirror = {char: i for i, char in enumerate(abeceda)}  # Creates mirror of lista

    def _randomsalt(self, szn, lenght):
        a = ""
        for i in range(lenght):
            a = a + secrets.choice(szn)
        return a

    def _mix_szn(self, szn):
        pocet = len(szn)
        for i in range(pocet):
            a = secrets.choice(szn)
            szn.remove(a)
            szn.insert(secrets.randbelow(len(szn)), a)
        return szn

    def _rotate(self, list_data, n):
        idx = self.mirror[n]
        if idx == 0: return list_data
        list_data = list_data[idx:] + list_data[:idx]
        self.mirror = {znak: i for i, znak in enumerate(list_data)}
        return list_data

    def _rotate_back(self, list_data, n):
        while not list_data[0] == n:
            a = list_data.pop(0)
            list_data.append(a)
        return list_data

    def sifrovat(self, data):
        time1 = time.time()  # Time measuring
        datalen = len(data) if len(data) > 0 else 1

        # < >Vigenere< >
        a, b, c = 0, 0, 0  # Three variables for keys
        vysledekl = []  # Final output from vigenere

        # Adding salt
        keey1elenght = min(len(self.key1) * len(self.key2) * len(self.key3), 100)  # Ensuring salt sequence length
        self.abeceda = list(self.abeceda)  # Makes list of characters
        data = self._randomsalt(self.abeceda, keey1elenght) + data  # Adds salt

        # Utf-8 coding
        utf = data.encode("utf-8")  # Code into numbers from 0 to 255
        data = list(utf)

        text = []
        lista = list(self.abeceda)  # Creates list for mixing
        self.mirror = {char: i for i, char in enumerate(lista)}  # Creates mirror of lista
        base161 = []  # Variable for output characters
        mirror2 = {znak: i for i, znak in enumerate(self.abeceda)}

        prev = 0
        for i, by in enumerate(data):
            current = by ^ prev
            data[i] = current
            prev = current

            text.append(self.abeceda[data[i]])  # Ensures support for UTF-8 including emojis

            # Rotating and mixing
            pozice = self.mirror[text[i]]  # Position of character before mixing
            posun1 = int((self.mirror[self.key1[a]]) % len(self.abeceda))  # Mix shift 1
            lista = self._rotate(lista, self.key1[a])  # Rotates mixing list
            posun2 = int((self.mirror[self.key2[b]] ^ self.mirror[self.key3[c]]) % len(self.abeceda))  # Mix shift 2

            znak1, znak2 = lista[posun1], lista[posun2]
            lista[posun1], lista[posun2] = lista[posun2], lista[posun1]  # Swaps characters
            self.mirror[znak1], self.mirror[znak2] = posun1, posun2

            lista = self._rotate(lista, self.abeceda[posun2])  # Rotates mixing list again

            vysledekl.append(lista[pozice])  # Gets ciphered character
            a = (a + 1) % len(self.key1)
            b = (b + 1) % len(self.key2)
            c = (c + 1) % len(self.key3)

            base1 = vysledekl[i]
            value = mirror2[base1]
            hnibble = (value >> 4) & 0x0F
            lnibble = value & 0x0F
            base161.append(self.supress[hnibble])
            base161.append(self.supress[lnibble])

        base162 = "".join(base161)
        elapsed_time = time.time() - time1
        return base162, elapsed_time

    def odsifrovat(self, data):
        time1 = time.time()  # Time measuring
        datalen = len(data) if len(data) > 0 else 1
        smirror = {znak: i for i, znak in enumerate(self.supress)}

        # < >Base16< >
        base161 = []

        try:
            for i in range(0, len(data), 2):
                hnibble = smirror[data[i]]
                lnibble = smirror[data[i + 1]]
                bytevalue = (hnibble << 4) | lnibble
                base161.append(self.abeceda[bytevalue])
        except (KeyError, IndexError):
            raise ValueError("Chyba při dešifrování Base16: Vstupní data neodpovídají nastavenému řetězci Supress!")

        base162 = "".join(base161)

        # < >Vigenere < >
        a, b, c = 0, 0, 0
        keey1elenght = min(len(self.key1) * len(self.key2) * len(self.key3), 100)

        vysledekl = []
        lista = list(self.abeceda)  # Dynamic alphabet
        lista2 = list(self.abeceda)  # Alphabet backup
        self.mirror = {char: i for i, char in enumerate(lista)}  # Creates mirror of lista

        for i in range(len(base162)):  # For every character
            posun1 = int((self.mirror[self.key1[a]]) % len(self.abeceda))
            lista = self._rotate(lista, self.key1[a])
            posun2 = (self.mirror[self.key2[b]] ^ self.mirror[self.key3[c]]) % len(self.abeceda)

            znak1 = lista[posun1]
            znak2 = lista[posun2]
            lista[posun1], lista[posun2] = lista[posun2], lista[posun1]
            self.mirror[znak1] = posun1
            self.mirror[znak2] = posun2

            lista = self._rotate(lista, self.abeceda[posun2])

            pozice = lista.index(base162[i])
            vysledekl.append(lista2[pozice])
            lista2 = list(lista)
            self.mirror = {char: i for i, char in enumerate(lista)}

            a = (a + 1) % len(self.key1)
            b = (b + 1) % len(self.key2)
            c = (c + 1) % len(self.key3)

        data = [self.abeceda.index(i) for i in vysledekl]

        # De-avalanching
        for i in range(len(data) - 1, 0, -1):
            data[i] = data[i] ^ data[i - 1]

        # Decoding UTF-8
        try:
            vysledek = bytes(data).decode("utf-8")
        except Exception:
            etext = [self.abeceda[i] for i in data]
            vysledek = "".join(etext)
            st.warning("Upozornění: UTF-8 dekódování selhalo (data mohou být poškozená). Zobrazen nouzový výstup.")

        vysledek = vysledek[keey1elenght:]
        elapsed_time = time.time() - time1
        return vysledek, elapsed_time


st.set_page_config(
    page_title="Ja1pr750 Cipher",
    page_icon="🔐",
    layout="wide"
)

st.sidebar.title("⚙️ Nastavení Klíčů")

# Default 256-character alphabet generator
DEFAULT_ABECEDA = "".join([chr(i) for i in range(256)])
DEFAULT_SUPRESS = "abcdefghijklmnop"

key1 = st.sidebar.text_input("Klíč 1 (Key1)", value="", type="password")
key2 = st.sidebar.text_input("Klíč 2 (Key2)", value="", type="password")
key3 = st.sidebar.text_input("Klíč 3 (Key3)", value="", type="password")

with st.sidebar.expander("🛠️ Pokročilé nastavení abecedy", expanded=False):
    supress_input = st.text_input("Supress (16 unikátních znaků)", value=DEFAULT_SUPRESS)
    abeceda_input = st.text_area("Abeceda (přesně 256 znaků)", value=DEFAULT_ABECEDA, height=120)

st.title("🔐 Šifrovací Nástroj (Ja1pr750)")
st.markdown("Aplikace pro bezpečné šifrování a dešifrování textových souborů `.txt`.")

# Validation checks
errors = []
if not key1 or not key2 or not key3:
    errors.append("Všechny tři klíče (Key1, Key2, Key3) musí být vyplněné.")
if len(supress_input) != 16 or len(set(supress_input)) != 16:
    errors.append("Supress řetězec musí mít přesně 16 unikátních znaků.")
if len(abeceda_input) != 256:
    errors.append(f"Abeceda musí mít přesně 256 znaků (současná délka: {len(abeceda_input)}).")

# Check if keys contain characters present in alphabet
if key1 and not all(char in abeceda_input for char in key1):
    errors.append("Key1 obsahuje znaky, které nejsou v definované abecedě.")
if key2 and not all(char in abeceda_input for char in key2):
    errors.append("Key2 obsahuje znaky, které nejsou v definované abecedě.")
if key3 and not all(char in abeceda_input for char in key3):
    errors.append("Key3 obsahuje znaky, které nejsou v definované abecedě.")

if errors:
    for err in errors:
        st.error(f"⚠️ {err}")
    st.stop()

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📁 Vstupní soubor")
    uploaded_file = st.file_uploader("Nahrajte textový soubor (.txt)", type=["txt"])

    operation = st.radio("Zvolte operaci:", ["Šifrovat", "Dešifrovat"], horizontal=True)

if uploaded_file is not None:
    try:
        content = uploaded_file.read().decode("utf-8")

        with col1:
            st.markdown("**Náhled vstupu:**")
            st.text_area("Obsah souboru", value=content[:500] + ("..." if len(content) > 500 else ""), height=150,
                         disabled=True)

        cipher = Ja1pr750(
            key1=key1,
            key2=key2,
            key3=key3,
            abeceda=abeceda_input,
            supress=supress_input
        )

        with col2:
            st.subheader("⚡ Výsledek")
            if st.button("🚀 Spustit zpracování", type="primary", use_container_width=True):
                with st.spinner("Zpracovávám data..."):
                    try:
                        if operation == "Šifrovat":
                            output_text, proc_time = cipher.sifrovat(content)
                            out_filename = uploaded_file.name.rsplit('.', 1)[0] + "_encrypted.txt"
                        else:
                            output_text, proc_time = cipher.odsifrovat(content)
                            out_filename = uploaded_file.name.rsplit('.', 1)[0] + "_decrypted.txt"

                        st.success(f"Hotovo za {proc_time:.4f} s!")
                        st.markdown("**Náhled výstupu:**")
                        st.text_area("Výsledek", value=output_text[:500] + ("..." if len(output_text) > 500 else ""),
                                     height=150, disabled=True)

                        st.download_button(
                            label="📥 Stáhnout výsledný .txt soubor",
                            data=output_text.encode("utf-8"),
                            file_name=out_filename,
                            mime="text/plain",
                            use_container_width=True
                        )
                    except Exception as e:
                        st.error(f"Chyba při zpracování: {str(e)}")

    except Exception as e:
        st.error(f"Chyba při čtení souboru: {str(e)}")
else:
    with col2:
        st.info("👈 Pro pokračování nahrajte `.txt` soubor v levém panelu.")
