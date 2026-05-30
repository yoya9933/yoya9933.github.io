use yew::prelude::*;

#[function_component(App)]
fn app() -> Html {
    html! {
        <main class="w-full max-w-3xl pt-8 md:pt-16">
            
            <header class="flex flex-col md:flex-row items-center gap-6 mb-12">
                <img src="https://via.placeholder.com/150/111/10b981?text=Me" alt="Avatar" 
                     class="w-32 h-32 md:w-36 md:h-36 rounded-full border-2 border-cyber-green shadow-[0_0_15px_rgba(16,185,129,0.3)]" />
                
                <div class="text-center md:text-left">
                    <h1 class="text-3xl md:text-5xl font-bold text-cyber-green mb-2">
                        { "> Hello, World._" }
                    </h1>
                    <h2 class="text-xl md:text-2xl text-slate-400">
                        { "I'm a Developer | Tech Enthusiast" }
                    </h2>
                </div>
            </header>

            <section class="bg-[#1e293b] rounded-lg border border-slate-700 overflow-hidden shadow-xl mb-12">
                
                <div class="bg-slate-800 px-4 py-2 flex items-center gap-2 border-b border-slate-700">
                    <div class="w-3 h-3 rounded-full bg-red-500"></div>
                    <div class="w-3 h-3 rounded-full bg-yellow-400"></div>
                    <div class="w-3 h-3 rounded-full bg-green-500"></div>
                    <span class="ml-2 text-xs text-slate-400 font-sans">{ "user@website: ~" }</span>
                </div>
                
                <div class="p-4 md:p-6 text-sm md:text-base leading-relaxed text-slate-300">
                    {/* 自我介紹 */}
                    <p class="mb-2"><span class="text-cyber-green">{ "user@website:~$ " }</span>{ "whoami" }</p>
                    <p class="mb-6 text-slate-100 pl-4 border-l-2 border-slate-600">
                        { "嗨！我是 yoya，一個熱愛挑戰與解決問題的開發者。" }<br/>
                        { "喜歡把酷炫的想法變成現實，例如這個由 Rust + WebAssembly 驅動的終端機網站！" }
                    </p>
                    
                    {/* 技能清單 */}
                    <p class="mb-2"><span class="text-cyber-green">{ "user@website:~$ " }</span>{ "ls -l skills/" }</p>
                    <div class="grid grid-cols-2 md:grid-cols-3 gap-2 text-slate-400 pl-4 mb-6">
                        <span>{ "- Rust (Wasm)" }</span>
                        <span>{ "- Yew Framework" }</span>
                        <span>{ "- HTML / CSS" }</span>
                        <span>{ "- Tailwind CSS" }</span>
                        <span>{ "- Git & GitHub" }</span>
                    </div>

                    {/* 目前狀態與目標 */}
                    <p class="mb-2"><span class="text-cyber-green">{ "user@website:~$ " }</span>{ "tail -f /var/log/status.log" }</p>
                    <p class="text-slate-100 pl-4 border-l-2 border-slate-600">
                        <span class="text-slate-400">{ "[INFO] " }</span>{ "目前狀態：尋找前端 / 全端開發的工作與合作機會中 🚀" }<br/>
                        <span class="text-slate-400">{ "[INFO] " }</span>{ "學習軌跡：持續挖掘 Rust 生態系與 Web 效能優化。" }<br/>
                        <span class="text-green-400">{ "[READY]" }</span>{ " 歡迎隨時與我建立連線！" }
                    </p>
                    
                    <p class="mt-6"><span class="text-cyber-green">{ "user@website:~$ " }</span><span class="animate-pulse bg-slate-400 w-2 h-4 inline-block align-middle"></span></p>
                </div>
            </section>

        </main>
    }
}

fn main() {
    yew::Renderer::<App>::new().render();
}