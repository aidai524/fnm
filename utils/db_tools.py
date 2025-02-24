from sqlalchemy import inspect, text
from config.database import engine, SessionLocal
from typing import Dict, List, Any, Optional
import json

def get_all_tables() -> List[str]:
    """
    获取数据库中所有表名
    """
    inspector = inspect(engine)
    return inspector.get_table_names()

def get_table_structure(table_name: str) -> Dict[str, Any]:
    """
    获取指定表的结构信息
    """
    inspector = inspect(engine)
    
    return {
        "columns": [
            {
                "name": column["name"],
                "type": str(column["type"]),
                "nullable": column["nullable"],
                "default": str(column["default"]) if column.get("default") else None,
            }
            for column in inspector.get_columns(table_name)
        ],
        "primary_key": inspector.get_pk_constraint(table_name)["constrained_columns"],
        "foreign_keys": [
            {
                "referred_table": fk["referred_table"],
                "referred_columns": fk["referred_columns"],
                "constrained_columns": fk["constrained_columns"],
            }
            for fk in inspector.get_foreign_keys(table_name)
        ],
        "indexes": inspector.get_indexes(table_name)
    }

def query_table(table_name: str, limit: int = 10, where: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    查询指定表的数据
    :param table_name: 表名
    :param limit: 返回的最大记录数
    :param where: WHERE子句的条件
    """
    with SessionLocal() as session:
        where_clause = f"WHERE {where}" if where else ""
        query = text(f"SELECT * FROM {table_name} {where_clause} LIMIT :limit")
        result = session.execute(query, {"limit": limit})
        return [dict(row._mapping) for row in result]

def print_table_info(table_name: str):
    """
    打印表的详细信息
    """
    structure = get_table_structure(table_name)
    
    print(f"\n{'='*50}")
    print(f"表名: {table_name}")
    print(f"{'='*50}")
    
    print("\n列信息:")
    print("-"*30)
    for column in structure["columns"]:
        print(f"列名: {column['name']}")
        print(f"类型: {column['type']}")
        print(f"可空: {column['nullable']}")
        print(f"默认值: {column['default']}")
        print("-"*30)
    
    if structure["primary_key"]:
        print("\n主键:", ", ".join(structure["primary_key"]))
    
    if structure["foreign_keys"]:
        print("\n外键关系:")
        for fk in structure["foreign_keys"]:
            print(f"- {','.join(fk['constrained_columns'])} -> "
                  f"{fk['referred_table']}({','.join(fk['referred_columns'])})")
    
    if structure["indexes"]:
        print("\n索引:")
        for idx in structure["indexes"]:
            print(f"- {idx['name']}: {', '.join(idx['column_names'])}"
                  f" ({'唯一索引' if idx['unique'] else '普通索引'})")

def print_table_data(table_name: str, limit: int = 10, where: Optional[str] = None):
    """
    打印表的数据
    """
    data = query_table(table_name, limit, where)
    if not data:
        print(f"\n表 {table_name} 没有数据")
        return
    
    print(f"\n表 {table_name} 的数据:")
    print("="*100)
    
    # 打印表头
    headers = list(data[0].keys())
    header_row = " | ".join(f"{h:<20}" for h in headers)
    print(header_row)
    print("-"*len(header_row))
    
    # 打印数据
    for row in data:
        row_str = " | ".join(f"{str(val):<20}" for val in row.values())
        print(row_str)

def main():
    """
    主函数，用于交互式查看数据库信息
    """
    tables = get_all_tables()
    
    print("\n可用的表:")
    for i, table in enumerate(tables, 1):
        print(f"{i}. {table}")
    
    while True:
        print("\n请选择操作:")
        print("1. 查看表结构")
        print("2. 查看表数据")
        print("3. 退出")
        
        choice = input("\n请输入选项编号: ")
        
        if choice == "3":
            break
        
        if choice in ["1", "2"]:
            print("\n可用的表:")
            for i, table in enumerate(tables, 1):
                print(f"{i}. {table}")
            
            table_index = int(input("\n请输入表的编号: ")) - 1
            if 0 <= table_index < len(tables):
                table_name = tables[table_index]
                
                if choice == "1":
                    print_table_info(table_name)
                else:
                    limit = int(input("请输入要显示的记录数 (默认10): ") or 10)
                    where = input("请输入WHERE条件 (可选): ").strip() or None
                    print_table_data(table_name, limit, where)
            else:
                print("无效的表编号")
        else:
            print("无效的选项")

if __name__ == "__main__":
    main() 