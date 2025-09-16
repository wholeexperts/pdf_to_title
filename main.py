import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
from utlies.pdf_to_text import pdf_to_text
from utlies.model_manager import ModelManager
from utlies.naming_manager import NamingManager
from utlies.api_key_manager import APIKeyManager


class PDFUploaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF 文件上传器")
        self.root.geometry("800x600")
        self.root.resizable(True, True)

        # 存储选中的文件路径
        self.selected_files = []
        
        # 初始化管理器
        self.api_key_manager = APIKeyManager()
        self.model_manager = None  # 不在初始化时创建模型管理器
        self.naming_manager = NamingManager()

        # 创建界面组件
        self.create_widgets()

    def create_widgets(self):
        # 标题
        title_label = tk.Label(self.root, text="请选择PDF 文件", font=("Arial", 14))
        title_label.pack(pady=10)

        # 配置区域
        config_frame = tk.LabelFrame(self.root, text="配置选项", padx=10, pady=10)
        config_frame.pack(fill=tk.X, padx=20, pady=5)
        
        # 模型选择
        model_frame = tk.Frame(config_frame)
        model_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(model_frame, text="模型提供商:").pack(side=tk.LEFT)
        self.provider_var = tk.StringVar(value="zhipu")
        self.provider_combo = ttk.Combobox(model_frame, textvariable=self.provider_var, 
                                          values=list(ModelManager.list_providers().keys()), 
                                          state="readonly", width=15)
        self.provider_combo.pack(side=tk.LEFT, padx=5)
        self.provider_combo.bind("<<ComboboxSelected>>", self.on_provider_change)
        
        tk.Label(model_frame, text="模型:").pack(side=tk.LEFT, padx=(20, 5))
        self.model_var = tk.StringVar(value="glm-4.5-flash")
        self.model_combo = ttk.Combobox(model_frame, textvariable=self.model_var, 
                                       state="readonly", width=20)
        self.model_combo.pack(side=tk.LEFT, padx=5)
        self.update_model_list()
        
        # API密钥按钮
        self.api_key_button = tk.Button(model_frame, text="🔑 设置API密钥", 
                                       command=self.set_api_key, 
                                       font=("Arial", 9))
        self.api_key_button.pack(side=tk.LEFT, padx=(10, 0))
        
        # 命名格式选择
        naming_frame = tk.Frame(config_frame)
        naming_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(naming_frame, text="命名格式:").pack(side=tk.LEFT)
        self.naming_var = tk.StringVar(value="title_author")
        naming_formats = {k: v["name"] for k, v in NamingManager.list_formats().items()}
        self.naming_combo = ttk.Combobox(naming_frame, textvariable=self.naming_var,
                                        values=list(naming_formats.keys()),
                                        state="readonly", width=20)
        self.naming_combo.pack(side=tk.LEFT, padx=5)
        
        # 选择文件按钮
        select_button = tk.Button(
            self.root,
            text="📂 选择 PDF 文件",
            command=self.select_pdfs,
            font=("Arial", 12),
            bg="#4CAF50",
            fg="white",
            padx=10,
            pady=5
        )
        select_button.pack(pady=10)

        # 文件列表显示框
        list_frame = tk.Frame(self.root)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.file_listbox = tk.Listbox(
            list_frame,
            yscrollcommand=scrollbar.set,
            font=("Courier", 10),
            selectmode=tk.EXTENDED,  # 支持多选删除
            bg="#f9f9f9"
        )
        self.file_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.file_listbox.yview)

        # 底部按钮区域
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=10)

        clear_button = tk.Button(
            button_frame,
            text="🗑️ 清空列表",
            command=self.clear_list,
            font=("Arial", 10),
            bg="#f44336",
            fg="white",
            padx=10
        )
        clear_button.pack(side=tk.LEFT, padx=5)

        process_button = tk.Button(
            button_frame,
            text="⚙️ 处理文件",
            command=self.process_files,
            font=("Arial", 10),
            bg="#2196F3",
            fg="white",
            padx=10
        )
        process_button.pack(side=tk.LEFT, padx=5)

        # 状态栏
        self.status_var = tk.StringVar()
        self.status_var.set("未选择任何文件")
        status_bar = tk.Label(
            self.root,
            textvariable=self.status_var,
            bd=1,
            relief=tk.SUNKEN,
            anchor=tk.W,
            font=("Arial", 9)
        )
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def on_provider_change(self, event=None):
        """当模型提供商改变时更新模型列表"""
        self.update_model_list()
    
    def update_model_list(self):
        """更新模型列表"""
        provider = self.provider_var.get()
        models = list(ModelManager.list_models(provider).keys())
        self.model_combo['values'] = models
        if models:
            self.model_combo.set(models[0])

    def set_api_key(self):
        """设置API密钥"""
        provider = self.provider_var.get()
        provider_name = ModelManager.list_providers().get(provider, provider)
        
        # 创建对话框
        dialog = tk.Toplevel(self.root)
        dialog.title(f"设置 {provider_name} API密钥")
        dialog.geometry("500x150")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()
        
        # 居中显示
        dialog.geometry("+%d+%d" % (self.root.winfo_rootx()+150, self.root.winfo_rooty()+150))
        
        # 输入框
        tk.Label(dialog, text=f"请输入 {provider_name} 的API密钥:", font=("Arial", 10)).pack(pady=(20, 5))
        
        api_key_var = tk.StringVar()
        # 如果已有密钥，显示部分隐藏的密钥
        existing_key = self.api_key_manager.get_key(provider)
        if existing_key:
            hidden_key = existing_key[:4] + "*" * (len(existing_key) - 8) + existing_key[-4:] if len(existing_key) > 8 else "*" * len(existing_key)
            api_key_var.set(hidden_key)
        
        entry = tk.Entry(dialog, textvariable=api_key_var, width=50, show="*")
        entry.pack(pady=5)
        entry.focus()
        
        # 显示/隐藏密码按钮
        show_var = tk.BooleanVar()
        
        def toggle_show():
            if show_var.get():
                entry.config(show="")
            else:
                entry.config(show="*")
        
        show_check = tk.Checkbutton(dialog, text="显示密钥", variable=show_var, command=toggle_show)
        show_check.pack()
        
        def save_key():
            api_key = api_key_var.get()
            # 如果输入的密钥和隐藏显示的密钥一样，说明没有更改
            if existing_key and api_key == (existing_key[:4] + "*" * (len(existing_key) - 8) + existing_key[-4:] if len(existing_key) > 8 else "*" * len(existing_key)):
                api_key = existing_key
            
            if not api_key:
                messagebox.showwarning("警告", "请输入API密钥")
                return
            
            self.api_key_manager.set_key(provider, api_key)
            dialog.destroy()
            messagebox.showinfo("成功", f"{provider_name} API密钥已保存")
        
        def cancel():
            dialog.destroy()
        
        # 按钮
        button_frame = tk.Frame(dialog)
        button_frame.pack(pady=20)
        
        tk.Button(button_frame, text="保存", command=save_key, bg="#4CAF50", fg="white").pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="取消", command=cancel).pack(side=tk.LEFT, padx=5)
        
        dialog.bind('<Return>', lambda e: save_key())
        dialog.bind('<Escape>', lambda e: cancel())

    def select_pdfs(self):
        """打开文件选择对话框，支持多选 PDF"""
        files = filedialog.askopenfilenames(
            title="选择一个或多个 PDF 文件",
            filetypes=[("PDF 文件", "*.pdf"), ("所有文件", "*.*")]
        )

        if not files:
            return

        # 添加到列表（去重）
        new_files = [f for f in files if f not in self.selected_files]
        self.selected_files.extend(new_files)

        # 更新 Listbox
        for f in new_files:
            self.file_listbox.insert(tk.END, os.path.basename(f))

        # 更新状态栏
        self.status_var.set(f"已选择 {len(self.selected_files)} 个文件")

    def clear_list(self):
        """清空文件列表"""
        self.selected_files.clear()
        self.file_listbox.delete(0, tk.END)
        self.status_var.set("已清空文件列表")

    def process_files(self):
        if not self.selected_files:
            messagebox.showwarning("警告", "请先选择 PDF 文件！")
            return

        try:
            # 更新模型管理器
            try:
                self.model_manager = ModelManager(
                    provider=self.provider_var.get(),
                    model_name=self.model_var.get()
                )
            except ValueError as e:
                messagebox.showerror("API密钥错误", str(e))
                self.set_api_key()
                return
            
            # 更新命名管理器
            self.naming_manager = NamingManager(
                format_type=self.naming_var.get()
            )
            
            total = len(self.selected_files)
            success_count = 0

            # 可选：禁用按钮防止重复点击
            self.root.config(cursor="wait")  # 显示等待光标
            self.root.update()  # 强制刷新界面

            for i, pdf_path in enumerate(self.selected_files):
                try:
                    # 假设这些函数你已实现
                    print(f"正在处理文件: {os.path.basename(pdf_path)}")
                    text = pdf_to_text(pdf_path)
                    print("前五百字符：{}".format(text[:500]))
                    print()
                    title, authors, year = self.model_manager.extract_info(text[:500])
                    print(f"Title: {title}")
                    print(f"Authors: {authors}")
                    print(f"Year: {year}")

                    if not authors:
                        raise ValueError("未能提取作者信息")

                    new_name = self.naming_manager.generate_filename(
                        pdf_path, title, authors, year
                    )
                    new_path = os.path.join(os.path.dirname(pdf_path), new_name)

                    # 重命名文件
                    os.rename(pdf_path, new_path)
                    print(new_name)
                    success_count += 1

                    # 可选：实时更新状态栏显示进度
                    self.status_var.set(f"处理中... ({i+1}/{total})")
                    self.root.update()  # 刷新界面

                except Exception as e:
                    messagebox.showerror("处理错误", f"文件 {os.path.basename(pdf_path)} 处理失败:\n{str(e)}")
                    continue

            # ✅✅✅ 处理结束：更新界面提示
            self.status_var.set(f"🎉 处理完成！成功 {success_count}/{total} 个文件")
            messagebox.showinfo("完成", f"文件处理完成！\n成功重命名 {success_count} 个文件")

            # 可选：清空当前列表（因为文件已重命名，旧路径失效）
            self.clear_list()

        except Exception as e:
            messagebox.showerror("严重错误", f"程序运行出错:\n{str(e)}")
            self.status_var.set("❌ 处理失败，请查看错误信息")
        finally:
            self.root.config(cursor="")  # 恢复正常光标

# 启动程序
if __name__ == "__main__":
    root = tk.Tk()
    app = PDFUploaderApp(root)
    root.mainloop()