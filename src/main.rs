use yew::prelude::*;

#[function_component(App)]
fn app() -> Html {
    html! {
        <main class="w-full max-w-3xl pt-8 md:pt-16">
            
            <header class="flex flex-col md:flex-row items-center gap-6 mb-12">
                <img src="https://github.com/yoya9933.png" alt="Avatar" 
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
                    <p class="mb-2"><span class="text-cyber-green">{ "user@website:~$ " }</span>{ "whoami" }</p>
                    <div class="mb-6 text-slate-100 pl-4 border-l-2 border-slate-600 space-y-2">
                        <p>{ "學歷：國立成功大學 水利及海洋工程學系、全校不分系學士學位學程（日間就讀中）" }</p>
                        <p>{ "地點：台南市中西區" }</p>
                        <p>{ "資歷：2~3年工作經驗" }</p>
                        <p>{ "希望職稱：軟體工程師 / 海軍官校軟體工程師" }</p>
                    </div>

                    <p class="mb-2"><span class="text-cyber-green">{ "user@website:~$ " }</span>{ "cat achievements.txt" }</p>
                    <div class="mb-6 text-slate-100 pl-4 border-l-2 border-slate-600 text-sm max-h-64 overflow-y-auto pr-2 scrollbar-thin scrollbar-thumb-slate-600 scrollbar-track-transparent">
                        <div class="mb-2 text-cyber-green font-semibold">{ "🏆 競賽佳績" }</div>
                        <ul class="list-disc list-inside mb-4 space-y-1 text-slate-300">
                            <li>{ "2025諾大師海洋大數據競賽 優選（冠軍）" }</li>
                            <li>{ "2025高通台灣AI黑客松競賽 季軍" }</li>
                            <li>{ "2025台灣海洋國際青年論壇 領航之星獎" }</li>
                            <li>{ "2024梅山36灣自行車挑戰賽 總成績05:18:13" }</li>
                            <li>{ "2023學校盃全國象棋團體錦標賽 冠軍" }</li>
                            <li>{ "2018國際運算思維挑戰賽 220分(PR94) / 195分(PR84)" }</li>
                            <li>{ "2016象棋主委盃暨中國石化杯 冠軍" }</li>
                            <li>{ "2015市長盃全國象棋錦標賽 / 象棋主委盃 亞軍" }</li>
                            <li>{ "2013卓越杯數學競賽 優選" }</li>
                        </ul>

                        <div class="mb-2 text-cyber-green font-semibold">{ "📜 專業證照" }</div>
                        <ul class="list-disc list-inside mb-4 space-y-1 text-slate-300">
                            <li>{ "ModelScope Agent Engineer 證照" }</li>
                            <li>{ "iFLY TEK Fine-tuning Engineer 證照" }</li>
                            <li>{ "iFLY TEK SPARK Prompt Engineer 證照" }</li>
                            <li>{ "ANT GROUP Agent Engineer 證照" }</li>
                            <li>{ "NVIDIA 透過Jetson Nano 開發人工智慧應用 證照" }</li>
                            <li>{ "浪潮信息 大模型開發工程師 證照" }</li>
                        </ul>

                        <div class="mb-2 text-cyber-green font-semibold">{ "🎓 榮譽獎項" }</div>
                        <ul class="list-disc list-inside mb-2 space-y-1 text-slate-300">
                            <li>{ "107, 108, 109, 110年度 高雄數位學園競賽活動表現優異" }</li>
                            <li>{ "107, 113學年度 成績優良獎" }</li>
                            <li>{ "109學年度 家長會長獎 / 校長獎" }</li>
                            <li>{ "112學年度 畢業成績優良 / 市長獎" }</li>
                        </ul>
                    </div>
                    
                    <p class="mb-2"><span class="text-cyber-green">{ "user@website:~$ " }</span>{ "ls -l skills/" }</p>
                    <div class="grid grid-cols-2 md:grid-cols-3 gap-2 text-slate-400 pl-4 mb-6">
                        <span>{ "- Rust (Wasm)" }</span>
                        <span>{ "- Yew Framework" }</span>
                        <span>{ "- HTML / CSS" }</span>
                        <span>{ "- Tailwind CSS" }</span>
                        <span>{ "- Git & GitHub" }</span>
                    </div>

                    <p class="mb-2"><span class="text-cyber-green">{ "user@website:~$ " }</span>{ "tail -f /var/log/status.log" }</p>
                    <p class="text-slate-100 pl-4 border-l-2 border-slate-600">
                        <span class="text-slate-400">{ "[INFO] " }</span>{ "目前狀態：尋找前端 / 全端開發的工作與合作機會中 " }<br/>
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