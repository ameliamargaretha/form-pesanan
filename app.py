import datetime
import os
import streamlit as st
import pandas as pd
from dataclasses import dataclass
from pull import send_email
from connect import p_db

PRODUK = sorted([x.strip() for x in open("./nama_produk.txt").readlines()])

st.beta_set_page_config(
    page_title="Grosir Pandai",
    page_icon="🧾",
)


@dataclass
class produk:
    nama_produk: str
    qty: int
    satuan: str  # slob, pcs
    notes: str
    tanggal_dipesan: str = datetime.datetime.now().strftime("%D %X")

    def get_dict(self):
        return {
            "nama": self.nama_produk,
            "qty": self.qty,
            "satuan": self.satuan,
            "notes": self.notes,
            "tanggal_dipesan": self.tanggal_dipesan,
        }


@dataclass
class pesenan:
    cart = []
    is_duplikat: bool = False

    def tambah(self, produk_):
        self.cart.append(produk_)

    def verify(self):
        self.cart = [a for a in self.cart if a]
        nama = [a.nama_produk for a in self.cart]
        if len(nama) < 1:
            print("stok produk masih kosong")
            st.warning("tidak ada jumlah produk")
        nama_s = pd.Series(nama)
        du = nama_s[nama_s.duplicated()]

        if len(du) == 0:
            return True, du
        else:
            return False, du

    def to_df(self):
        v = self.verify()
        if v[0]:
            p = [a.get_dict() for a in self.cart]
            st.success(f"sukses menambahkan {len(self.cart)} produk")
            return pd.DataFrame(p)
        else:
            print(v[1].values)
            st.error("terdapat produk yang sama di dalam cart")
            st.error(f"produknya adalah {v[1].values}")
            st.stop()

    def __len__(self):
        return len(self.cart)


def menu_produk_pilihan(id):
    h = st.selectbox(f"produk_{id}", PRODUK)
    qty = st.number_input(f"berapa_{id}", step=1.0, max_value=9e10, min_value=0.0)
    satuan = st.selectbox(f"satuan_{id}", ["SLOB", "PCS", "none"])
    notes = st.text_area(f"NOTES_{id}")
    st.markdown("---")
    if qty >= 1:
        return produk(h, int(qty), satuan, notes)


def val_unique_code(code):
    if len(code) == 12:
        return True
    return False


def main():
    st.title("Grosir ")
    st.header("Order By")
    order_by = st.radio(" ", options=["manual", "aplikasi"])

    st.header("Nama Sales")
    nama_sales = st.text_input("SALES")
    st.header("Nama Toko")
    nama_toko = st.text_input("TOKO")

    st.header("Unique Code")
    code = st.text_input("CODE")
    if not val_unique_code(code):
        st.warning("masukkan code dengan baik dan benar, untuk melanjutkan")
        st.stop()

    st.header("Nomor Telepon Toko")
    no = st.text_input("TELEPON")

    pesenan_produk = pesenan()
    st.header("Pilih Produk")
    c = 0
    n_produk = st.number_input(
        "JUMLAH PRODUK", step=1, min_value=1, max_value=len(PRODUK)
    )
    st.markdown("---")
    for n in range(n_produk):
        pesenan_produk.tambah(menu_produk_pilihan(n))
    print("n_pesenan", len(pesenan_produk))
    su = st.button("submit")
    if su:
        df = pesenan_produk.to_df()
        df["nama_toko"] = nama_toko
        df["nama_sales"] = nama_sales
        df["id"] = code
        df["nomor_telepon"] = code
        df["order_by"] = order_by
        st.write("konfirmasi pembelian produk")
        st.write(df)
        df.fillna("none", inplace=True)
        p_db.insert_many(df.to_dict("records")) # potential trouble here
        temp_df = pd.DataFrame(list(p_db.find({}, {'_id':0})))
        temp_df.drop_duplicates(inplace=True)
        temp_df.to_csv('temp.csv')
        send_email('./temp.csv')
        del temp_df
        os.system('rm ./temp.csv')
        st.warning("anda dapat menutup tab ini")


if __name__ == "__main__":
    main()
