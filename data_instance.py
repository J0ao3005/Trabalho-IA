import xml.etree.ElementTree as ET
from datetime import datetime
import os

def read_ros_instance(file_path):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Arquivo não encontrado: {file_path}")

    tree = ET.parse(file_path)
    root = tree.getroot()

    def get_tag(elem):
        return elem.tag.split('}')[-1]

    data = {
        "employees": [],
        "shift_types": [],
        "days_count": 0,
        "cover_requirements": {}, 
        "days_off": {},
        "shift_on_requests": {}, 
        "shift_off_requests": {} 
    }

    # 1. Período, Funcionários e Turnos
    start_date = None
    end_date = None
    
    for elem in root.iter():
        tag = get_tag(elem)
        if tag == "StartDate":
            start_date = datetime.strptime(elem.text, "%Y-%m-%d")
        elif tag == "EndDate":
            end_date = datetime.strptime(elem.text, "%Y-%m-%d")
        elif tag == "Employee":
            emp_id = elem.get("ID")
            if emp_id and emp_id not in data["employees"]:
                data["employees"].append(emp_id)
        elif tag == "Shift":
            s_id = elem.get("ID")
            if s_id and s_id not in data["shift_types"]:
                data["shift_types"].append(s_id)

    # 2. Dias
    if start_date and end_date:
        data["days_count"] = (end_date - start_date).days + 1
    else:
        data["days_count"] = 30 

    # 3. Demanda
    cover_reqs = None
    for possible_tag in ["CoverRequirements", "coverRequirements"]:
        found = root.find(f".//{{*}}{possible_tag}")
        if found is None: found = root.find(f".//{possible_tag}")
        if found is not None: 
            cover_reqs = found
            break
            
    if cover_reqs is not None:
        for date_cover in cover_reqs:
            day_idx = -1
            for child in date_cover:
                if get_tag(child) == "Day": day_idx = int(child.text)
            if day_idx != -1:
                if day_idx not in data["cover_requirements"]:
                    data["cover_requirements"][day_idx] = {}
                for child in date_cover:
                    if get_tag(child) == "Cover":
                        shift, min_val = None, 0
                        for info in child:
                            if get_tag(info) == "Shift": shift = info.text
                            if get_tag(info) == "Min": min_val = int(info.text)
                        if shift:
                            data["cover_requirements"][day_idx][shift] = min_val

    # 4. Pedidos (ShiftOff e ShiftOn)
    for elem in root.iter():
        tag = get_tag(elem)
        
        # --- ShiftOff (Pedido para EVITAR turno) ---
        if tag == "ShiftOff":
            emp, day, shift = None, None, None
            for child in elem:
                if get_tag(child) == "EmployeeID": emp = child.text
                if get_tag(child) == "Day": day = int(child.text)
                if get_tag(child) == "Shift": shift = child.text
            
            if emp and day is not None and shift:
                # Se não existir a chave, cria lista vazia
                if (emp, day) not in data["shift_off_requests"]:
                    data["shift_off_requests"][(emp, day)] = []
                # Adiciona o turno à lista de indesejados
                data["shift_off_requests"][(emp, day)].append(shift)

        # --- ShiftOn (Pedido para TRABALHAR) ---
        elif tag == "ShiftOn":
            emp, day, shift = None, None, None
            for child in elem:
                if get_tag(child) == "EmployeeID": emp = child.text
                if get_tag(child) == "Day": day = int(child.text)
                if get_tag(child) == "Shift": shift = child.text
            
            if emp and day is not None and shift:
                data["shift_on_requests"][(emp, day)] = shift

    print(f"DEBUG PARSER: {len(data['shift_on_requests'])} ShiftOn e {len(data['shift_off_requests'])} ShiftOff encontrados.")
    return data