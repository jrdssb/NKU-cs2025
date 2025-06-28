#add message to fish.py
#R11 message
#add another message to fish.py
import pandas as pd
import webbrowser
from http.server import SimpleHTTPRequestHandler
from socketserver import TCPServer
import os
import json

# 配置参数
CSV_FILE = "C:/Users/DELL/Desktop/dasanxia/se/data/se-data/Fish.csv"
OUTPUT_HTML = "Fish.html"
PORT = 8000


def main():
    # 读取CSV数据（保持原有验证逻辑）

    # 创建HTML文件
    html_template = f'''
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>鱼类数据可视化</title>
        <script src="https://d3js.org/d3.v7.min.js"></script>
        <style>
            .container {{
                max-width: 1280px;
                margin: 0 auto;
                padding: 0 20px;
            }}
            body {{
                margin: 20px; 
                font-family: "Microsoft YaHei", Arial;
                background-color: #f0f0f0;
            }}
            .axis line, .axis path {{
                stroke: #666; 
                stroke-width: 0.5;
            }}
            .axis text {{
                font-size: 12px; 
                fill: #333;
            }}
            .legend-item {{
                cursor: pointer; 
                margin: 0 20px; 
                display: inline-block;
                white-space: nowrap;
                padding: 5px;
                border-radius: 3px;
                transition: background-color 0.2s;
            }}
            #tooltip {{
                position: absolute; 
                padding: 12px; 
                background: rgba(255, 255, 255, 0.95); 
                border: 1px solid #ccc; 
                border-radius: 5px;
                pointer-events: none; 
                font-size: 13px; 
                box-shadow: 2px 2px 8px rgba(0,0,0,0.1);
                min-width: 180px;
            }}
            .chart-title {{
                text-align: center;
                color: #2c3e50;
                margin: 20px 0;
                font-size: 24px;
            }}
            .axis-label {{
                font-size: 14px;
                fill: #333;
            }}
            circle {{
                opacity: 0.7;
                transition: opacity 0.3s;
                stroke-width: 0;
            }}
            circle:hover {{
                stroke: #333;
                stroke-width: 2;
            }}
            .control-panel {{
                text-align: center;
                margin: 20px 0;
            }}
            .size-control {{
                display: inline-block;
                margin: 0 10px;
                padding: 8px 15px;
                border: 1px solid #ddd;
                border-radius: 4px;
                cursor: pointer;
                transition: all 0.2s;
            }}
            .size-control.active {{
                background: #007bff;
                color: white;
                border-color: #007bff;
            }}
            /* 修改统计块样式 */
            #statistics {{
                margin: 40px auto;
                padding: 20px;
                background: white;
                border-radius: 8px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            }}
            #stats-table {{
                width: 100%;
                border-collapse: collapse;
                margin-top: 10px;
            }}
            #stats-table th, #stats-table td {{
                padding: 10px;
                text-align: left;
                border-bottom: 1px solid #ddd;
            }}
            #stats-table th {{
                background-color: #f8f9fa;
            }}
            #stats-table tr:hover {{
                background-color: #f1f1f1;
            }}
            svg {{
                display: block;
                margin: 0 auto;
                background: white;
                border-radius: 8px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            }}
        </style>

    </head>
    <body>
        <h1 class="chart-title">鱼类数据</h1>


        
        <div id="tooltip"></div>
        <div id="statistics">
            <h2 class="chart-title">统计信息</h2>
            <table id="stats-table">
                <thead>
                    <tr>
                        <th>物种</th>
                        <th>数量</th>
                        <th>平均宽度 (cm)</th>
                        <th>平均重量 (g)</th>
                        <th>平均Length1(cm)</th>
                        <th>平均Length2(cm)</th>
                        <th>平均Length3(cm)</th>
                    </tr>
                </thead>
                <tbody></tbody>
            </table>
        </div>
        <div class="control-panel">
            <div class="size-control active" data-dim="length1">Length1</div>
            <div class="size-control" data-dim="length2">Length2</div>
            <div class="size-control" data-dim="length3">Length3</div>
        </div>
        <div id="legend"></div>
            <!-- 新增统计块 -->
        <script>
            // 新增状态变量
            let currentSizeDimension = 'length1';
            let hiddenSpecies = new Set(); // 存储被隐藏的物种

            d3.csv("Fish.csv", d3.autoType).then(rawData => {{
                // 数据预处理
                const processedData = rawData.map(d => ({{
                    Species: d.Species,
                    width: d['Width(cm)'],
                    weight: d['Weight(g)'],
                    length1: d['Length1(cm)'],
                    length2: d['Length2(cm)'],
                    length3: d['Length3(cm)'],
                    height: d['Height(cm)']
                }})).filter(d => 
                    !isNaN(d.width) && 
                    !isNaN(d.weight) &&
                    d.width > 0 &&
                    d.weight > 0
                );
                            // 新增统计数据处理
            const speciesGroups = d3.group(processedData, d => d.Species);
            const statsData = Array.from(speciesGroups, ([species, records]) => ({{
                Species: species,
                Count: records.length,
                AvgWidth: d3.mean(records, d => d.width),
                AvgWeight: d3.mean(records, d => d.weight),
                AvgLength1: d3.mean(records, d => d.length1),
                AvgLength2: d3.mean(records, d => d.length2),
                AvgLength3: d3.mean(records, d => d.length3)
            }}));

            // 渲染统计表格
            const statsTable = d3.select("#stats-table tbody");
            statsTable.selectAll("tr")
                .data(statsData)
                .join("tr")
                .html(d => `
                    <td>${{d.Species}}</td>
                    <td>${{d.Count}}</td>
                    <td>${{d.AvgWidth.toFixed(2)}}</td>
                    <td>${{d.AvgWeight.toFixed(2)}}</td>
                    <td>${{d.AvgLength1.toFixed(2)}}</td>
                    <td>${{d.AvgLength2.toFixed(2)}}</td>
                    <td>${{d.AvgLength3.toFixed(2)}}</td>
                `);

                // 计算点的大小（保持原逻辑）
                const sizeValues = processedData.map(d => d.length1);
                const sizeExtent = d3.extent(sizeValues);

                // 设置比例尺
                const width = 1280, height = 680;
                const margin = {{ top: 40, right: 50, bottom: 60, left: 70 }};

                // X轴改为Width
                const x = d3.scaleLinear()
                    .domain(d3.extent(processedData, d => d.width))
                    .range([margin.left, width - margin.right])
                    .nice();

                // Y轴改为Weight
                const y = d3.scaleLinear()
                    .domain(d3.extent(processedData, d => d.weight))
                    .range([height - margin.bottom, margin.top])
                    .nice();

                // 改为统一使用sizeScale
                // 动态计算初始size比例尺
                const initialSizeValues = processedData.map(d => d[currentSizeDimension]);
                const size = d3.scaleSqrt()
                    .domain(d3.extent(initialSizeValues))
                    .range([3, 25]);

                const color = d3.scaleOrdinal()
                    .domain(Array.from(new Set(processedData.map(d => d.Species))))
                    .range(d3.schemeTableau10);

                // 创建SVG画布
                const svg = d3.select("body").append("svg")
                    .attr("width", width)
                    .attr("height", height)
                    .style("background", "white")
                    .style("border-radius", "8px")
                    .style("box-shadow", "0 2px 8px rgba(0,0,0,0.1)");
                d3.selectAll(".size-control").on("click", function() {{
                    // 切换active状态
                    d3.selectAll(".size-control").classed("active", false);
                    d3.select(this).classed("active", true);
                
                    // 更新当前尺寸维度
                    currentSizeDimension = d3.select(this).attr("data-dim");
                
                    // 过滤可见数据（排除隐藏物种）
                    const visibleData = processedData.filter(d => !hiddenSpecies.has(d.Species));
                    
                    // 处理空数据集的情况
                    const safeExtent = (data) => data.length > 0 ? d3.extent(data) : [0, 1];
                    
                    // 更新比例尺domain（基于可见数据）
                    const newSizeValues = visibleData.map(d => d[currentSizeDimension]);
                    size.domain(safeExtent(newSizeValues));
                
                    // 更新所有圆点的半径（包括隐藏的，但视觉上不可见）
                    circles.transition()
                        .duration(300)
                        .attr("r", d => size(d[currentSizeDimension]));
                }});
                const circles = svg.selectAll("circle")
                    .data(processedData)
                    .join("circle")
                    .attr("cx", d => x(d.width))
                    .attr("cy", d => y(d.weight))
                    .attr("r", d => size(d[currentSizeDimension]))  // 动态属性
                    .style("fill", d => color(d.Species))
                    .on("mouseover", showTooltip)
                    .on("mouseout", hideTooltip);

                // 绘制坐标轴
                svg.append("g")
                    .attr("class", "x-axis")
                    .attr("transform", `translate(0,${{height - margin.bottom}})`)
                    .call(d3.axisBottom(x))
                    .append("text")
                    .attr("class", "axis-label")
                    .attr("x", width/2)
                    .attr("y", 35)
                    .style("text-anchor", "middle")
                    .text("体宽 Width (cm)");  // 修改X轴标签

                svg.append("g")
                    .attr("class", "y-axis")
                    .attr("transform", `translate(${{margin.left}},0)`)
                    .call(d3.axisLeft(y))
                    .append("text")
                    .attr("class", "axis-label")
                    .attr("transform", "rotate(-90)")
                    .attr("x", -height/2)
                    .attr("y", -50)
                    .style("text-anchor", "middle")
                    .text("重量 Weight (g)");  // 修改Y轴标签

                // 创建图例（保持原逻辑）
                const legend = d3.select("#legend")
                    .style("text-align", "center")
                    .selectAll(".legend-item")
                    .data(color.domain())
                    .join("div")
                    .attr("class", "legend-item")
                    .on("click", toggleVisibility);

                legend.append("span")
                    .style("display", "inline-block")
                    .style("width", "14px")
                    .style("height", "14px")
                    .style("background-color", color)
                    .style("margin-right", "6px")
                    .style("border-radius", "3px");

                legend.append("span")
                    .text(d => d)
                    .style("font-size", "14px")
                    .style("color", "#444");

                // 交互功能
                function showTooltip(event, d) {{
                    d3.select(this)
                        .style("opacity", 1)
                        .style("stroke", "#333");

                    d3.select("#tooltip")
                        .html(`
                            <div style="margin-bottom:6px;font-weight:bold;color:${{color(d.Species)}};">
                                ${{d.Species}}
                            </div>
                            <div>体宽: ${{d.width.toFixed(2)}} cm</div>
                            <div>重量: ${{d.weight.toFixed(2)}} g</div>
                            <div>Length1: ${{d.length1.toFixed(2)}} cm</div>
                            <div>Length2: ${{d.length2.toFixed(2)}} cm</div>
                            <div>Length3: ${{d.length3.toFixed(2)}} cm</div>
                        `)
                        .style("left", `${{event.pageX + 15}}px`)
                        .style("top", `${{event.pageY - 15}}px`)
                        .style("opacity", 1);
                }}

                function hideTooltip() {{
                    d3.select(this)
                        .style("opacity", 0.7)
                        .style("stroke", "none");
                    d3.select("#tooltip").style("opacity", 0);
                }}

                function toggleVisibility(event, s) {{
                    const isActive = d3.select(this).classed("active");
                    d3.select(this).classed("active", !isActive);

                    // 更新隐藏物种集合
                    if (isActive) {{
                        hiddenSpecies.delete(s);
                    }} else {{
                        hiddenSpecies.add(s);
                    }}

                    // 过滤可见数据
                    const visibleData = processedData.filter(d => !hiddenSpecies.has(d.Species));

                    // 安全处理空数据集
                    const safeExtent = (data, accessor) => 
                        data.length > 0 ? d3.extent(data, accessor) : [0, 1];

                    // 更新坐标轴domain
                    x.domain(safeExtent(visibleData, d => d.width)).nice();
                    y.domain(safeExtent(visibleData, d => d.weight)).nice();

                    // 更新坐标轴显示（带过渡动画）
                    svg.select(".x-axis")
                        .transition()
                        .duration(300)
                        .call(d3.axisBottom(x).tickSizeOuter(0));

                    svg.select(".y-axis")
                        .transition()
                        .duration(300)
                        .call(d3.axisLeft(y).tickSizeOuter(0));

                    // 更新所有数据点的位置和透明度
                    circles
                        .transition()
                        .duration(300)
                        .attr("cx", d => x(d.width))
                        .attr("cy", d => y(d.weight))
                        .style("opacity", d => hiddenSpecies.has(d.Species) ? 0 : 0.7);
                }}
            }});
        </script>
    </body>
    </html>
    '''

    # 保存文件
    try:
        with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
            f.write(html_template)

    except Exception as e:
        print("文件保存失败：")
        print(str(e))
        return

    # 启动服务器
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    handler = SimpleHTTPRequestHandler
    httpd = TCPServer(("", PORT), handler)

    print(f"服务已启动，请访问：http://localhost:{PORT}/{OUTPUT_HTML}")
    print("按 Ctrl+C 停止服务器")
    webbrowser.open(f"http://localhost:{PORT}/{OUTPUT_HTML}")

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n正在关闭服务器...")
        httpd.server_close()

if __name__ == "__main__":
    main()