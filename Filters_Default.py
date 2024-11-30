import re
import pandas as pd



class Nag_filter:
    @staticmethod
    def filter_interface_status(output):
        """
        "show int eth status" buyrug'i natijasini filtrlash:
        - Link/Protocol = DOWN/DOWN
        - Alias Name = bo'sh
        - Type = G-TX
        """
        # Chiqimni qatorlarga ajratish
        lines = output.strip().split("\n")

        # "Interface  Link/Protocol" qatorini topib, undan keyin boshlanadigan ma'lumotlarni olish
        start_idx = None
        for i, line in enumerate(lines):
            if line.strip().startswith("Interface"):
                start_idx = i
                break

        if start_idx is None:
            return []  # Agar kerakli qator topilmasa, bo‘sh natija qaytarish

        # Faqat kerakli qatorlardan keyingi qatorlarni ishlatamiz
        data_lines = lines[start_idx + 1:]

        # Qo'shimcha qatorlar, masalan "red_team#" ni olib tashlash
        data_lines = [line for line in data_lines if line.strip() and not line.strip().startswith("red_team")]

        # Ustun nomlarini aniqlash
        headers = ['Interface', 'Link/Protocol', 'Speed', 'Duplex', 'Vlan', 'Type', 'Alias Name']
        rows = []

        for line in data_lines:
            # Har bir qatorni ustunlarga bo‘lish
            columns = re.split(r'\s{2,}', line)
            if len(columns) == len(headers):  # Faqat ustunlar soni to‘g‘ri bo‘lsa qo‘shamiz
                rows.append(columns)

        # Pandas DataFrame yaratish
        if not rows:  # Agar hech qanday ma'lumot bo‘lmasa, bo‘sh natija qaytaramiz
            return []
        df = pd.DataFrame(rows, columns=headers)

        # Filtrlash shartlari
        filtered_df = df[(df["Link/Protocol"] == "A-DOWN/DOWN") & (df["Alias Name"] == "") & (df["Type"] == "G-TX")]

        # Natijani ro'yxat sifatida qaytarish
        return filtered_df.to_dict(orient="records")

    def filter_vlans(vlan_output, vlan_id=None, vlan_name=None):
        """
        VLAN ma'lumotlarini filtrlash:
        - vlan_id: Agar berilgan bo'lsa, faqat shu ID bilan mos VLAN qaytariladi.
        - vlan_name: Agar berilgan bo'lsa, faqat shu nom bilan mos VLAN qaytariladi.
        """
        lines = vlan_output.strip().split("\n")

        start_idx = None
        for i, line in enumerate(lines):
            if line.strip().startswith("VLAN Name"):
                start_idx = i
                break

        if start_idx is None:
            return []

        data_lines = lines[start_idx + 1:]
        headers = ['VLAN ID', 'VLAN Name', 'Type', 'Media', 'Ports']
        rows = []

        current_row = None
        for line in data_lines:
            if not line.strip() or line.startswith('----'):
                continue

            if re.match(r'^\d+', line.strip()):
                if current_row:
                    rows.append(current_row)
                columns = re.split(r'\s{2,}', line.strip(), maxsplit=4)
                current_row = dict(zip(headers, columns))
            elif current_row and "Ports" in current_row:
                current_row["Ports"] += f" {line.strip()}"

        if current_row:
            rows.append(current_row)

        df = pd.DataFrame(rows)
        if vlan_id:
            df = df[df["VLAN ID"] == str(vlan_id)]
        if vlan_name:
            df = df[df["VLAN Name"].str.contains(vlan_name, case=False)]

        return df.to_dict(orient="records")



class DCN_filter:
    @staticmethod
    def filter_interface_status(output):
        """
        "show int eth status" buyrug'i natijasini filtrlash:
        - Link/Protocol = DOWN/DOWN
        - Alias Name bo'sh
        - Type = G-TX
        """
        # Chiqimni qatorlarga ajratish
        lines = output.strip().split("\n")

        # "Interface  Link/Protocol" qatorini topib, undan keyin boshlanadigan ma'lumotlarni olish
        start_idx = None
        for i, line in enumerate(lines):
            if line.strip().startswith("Interface"):
                start_idx = i
                break

        if start_idx is None:
            return []  # Agar kerakli qator topilmasa, bo‘sh natija qaytarish

        # Faqat kerakli qatorlardan keyingi qatorlarni ishlatamiz
        data_lines = lines[start_idx + 1:]

        # Qo'shimcha qatorlar, masalan "red_team#" ni olib tashlash
        data_lines = [line for line in data_lines if line.strip() and not line.strip().startswith("red_team")]

        # Ustun nomlarini aniqlash
        headers = ['Interface', 'Link/Protocol', 'Speed', 'Duplex', 'Vlan', 'Type', 'Alias Name']
        rows = []

        for line in data_lines:
            # Har bir qatorni ustunlarga bo‘lish
            columns = re.split(r'\s{2,}', line)
            if len(columns) == len(headers):  # Faqat ustunlar soni to‘g‘ri bo‘lsa qo‘shamiz
                rows.append(columns)

        # Pandas DataFrame yaratish
        if not rows:  # Agar hech qanday ma'lumot bo‘lmasa, bo‘sh natija qaytaramiz
            return []
        df = pd.DataFrame(rows, columns=headers)

        # Filtrlash shartlari
        filtered_df = df[(df["Link/Protocol"] == "DOWN/DOWN") & (df["Alias Name"] == "") & (df["Type"] == "G-TX")]

        # Natijani ro'yxat sifatida qaytarish
        return filtered_df.to_dict(orient="records")

    def filter_vlans(vlan_output, vlan_id=None, vlan_name=None):
        """
        VLAN ma'lumotlarini filtrlash:
        - vlan_id: Agar berilgan bo'lsa, faqat shu ID bilan mos VLAN qaytariladi.
        - vlan_name: Agar berilgan bo'lsa, faqat shu nom bilan mos VLAN qaytariladi.
        """
        lines = vlan_output.strip().split("\n")

        start_idx = None
        for i, line in enumerate(lines):
            if line.strip().startswith("VLAN Name"):
                start_idx = i
                break

        if start_idx is None:
            return []

        data_lines = lines[start_idx + 1:]
        headers = ['VLAN ID', 'VLAN Name', 'Type', 'Media', 'Ports']
        rows = []

        current_row = None
        for line in data_lines:
            if not line.strip() or line.startswith('----'):
                continue

            if re.match(r'^\d+', line.strip()):
                if current_row:
                    rows.append(current_row)
                columns = re.split(r'\s{2,}', line.strip(), maxsplit=4)
                current_row = dict(zip(headers, columns))
            elif current_row and "Ports" in current_row:
                current_row["Ports"] += f" {line.strip()}"

        if current_row:
            rows.append(current_row)

        df = pd.DataFrame(rows)
        if vlan_id:
            df = df[df["VLAN ID"] == str(vlan_id)]
        if vlan_name:
            df = df[df["VLAN Name"].str.contains(vlan_name, case=False)]

        return df.to_dict(orient="records")

class TP_Link:
    @staticmethod
    def filter_interface_status_tp_link(output):
        lines = output.strip().split("\n")

        start_idx = None
        for i, line in enumerate(lines):
            if line.strip().startswith("Port"):
                start_idx = i
                break

        if start_idx is None:
            return []

        data_lines = lines[start_idx + 1:]
        headers = ['Port', 'Status', 'Speed', 'Duplex', 'FlowCtrl', 'Active-Medium']
        rows = []

        for line in data_lines:
            if line.strip():
                columns = re.split(r'\s{2,}', line.strip())
                if len(columns) == len(headers):
                    rows.append(columns)

        if not rows:
            return []
        df = pd.DataFrame(rows, columns=headers)

        filtered_df = df[
            (df["Status"] == "LinkDown") &
            (df["Active-Medium"] == "Copper")
            ]

        if filtered_df.empty:
            return []

        filtered_df.loc[:, "Port"] = filtered_df["Port"].str.replace(r"^Gi", "", regex=True)

        return filtered_df.to_dict(orient="records")

    def filter_interfaces_no_descr_or_shut_tplink(config_output):
        """
        TP-Link switch konfiguratsiyasidan interfeyslarni filtrlash:
        - Interfeysda `description` yo'q bo'lishi kerak.
        - Interfeysda `shutdown` bo'lmasligi kerak.
        """
        # Chiqimni qatorlarga ajratish
        lines = config_output.strip().split("\n")

        # Interfeys bloklarini saqlash
        interfaces = []
        current_interface = None
        for line in lines:
            line = line.strip()

            # Interfeys boshlanishini aniqlash
            if line.startswith("interface"):
                # Avvalgi interfeysni tugatish va ro'yxatga qo'shish
                if current_interface:
                    interfaces.append(current_interface)
                current_interface = {
                    "interface": line.split(" ")[-1],
                    "has_description": False,
                    "has_shutdown": False
                }
            elif current_interface:
                # Interfeysda `description` mavjudligini aniqlash
                if line.startswith("description"):
                    current_interface["has_description"] = True
                # Interfeysda `shutdown` mavjudligini aniqlash
                elif line.startswith("shutdown"):
                    current_interface["has_shutdown"] = True

        # Oxirgi interfeysni ro'yxatga qo'shish
        if current_interface:
            interfaces.append(current_interface)

        # Filtrlash: description va shutdown mavjud bo'lmagan interfeyslarni olish
        filtered_interfaces = [
            iface for iface in interfaces
            if not iface["has_description"] and iface["has_shutdown"]
        ]

        # Natijani qaytarish
        return [{"interface": iface["interface"]} for iface in filtered_interfaces]