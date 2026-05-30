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
                    <p class="mb-2"><span class="text-cyber-green">{ "user@website:~$ " }</span>{ "cat about.txt" }</p>
                    <p class="mb-6 text-slate-100 pl-4 border-l-2 border-slate-600">
                        { "你好！我是 yoya。這是我用 Rust (WebAssembly) 重寫的終端機風格網站！" }<br/>
                        { "對寫程式與解決問題充滿熱情，現在這整個畫面是由 Yew 框架動態渲染的。" }
                    </p>
                    
                    <p class="mb-2"><span class="text-cyber-green">{ "user@website:~$ " }</span>{ "ls -l skills/" }</p>
                    <div class="grid grid-cols-2 md:grid-cols-3 gap-2 text-slate-400 pl-4">
                        <span>{ "- Rust (Wasm)" }</span>
                        <span>{ "- Yew Framework" }</span>
                        <span>{ "- HTML / CSS" }</span>
                        <span>{ "- Tailwind CSS" }</span>
                        <span>{ "- Git & GitHub" }</span>
                    </div>
                    
                    <p class="mt-6"><span class="text-cyber-green">{ "user@website:~$ " }</span><span class="animate-pulse bg-slate-400 w-2 h-4 inline-block align-middle"></span></p>
                </div>
            </section>

        </main>
    }
}

fn main() {
    yew::Renderer::<App>::new().render();
}