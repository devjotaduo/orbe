function Ft() {
  var ct, dt, ut, ft;
  const { React: e, antd: j, antdIcons: Y, getApiUrl: X, getApiToken: U } = window.QwenPaw.host, {
    Card: G,
    Table: M,
    Tag: $,
    Typography: Te,
    Space: W,
    Button: T,
    Input: Z,
    Radio: ve,
    Collapse: Kt,
    Descriptions: le,
    Tooltip: Ke,
    Spin: he,
    message: qe,
    theme: Ye
  } = j, { Text: V } = Te, { TextArea: gt } = Z, { useState: C, useMemo: Ee, useCallback: R, useRef: qt } = e, {
    InfoCircleOutlined: ze,
    DownOutlined: Xe,
    RightOutlined: yt,
    CheckCircleOutlined: Oe,
    FieldTimeOutlined: Pe,
    FileTextOutlined: Ge
  } = Y || {};
  function Ve(t) {
    var i, d;
    const n = (d = (i = t == null ? void 0 : t.content) == null ? void 0 : i[0]) == null ? void 0 : d.data, o = n == null ? void 0 : n.arguments;
    if (typeof o == "string")
      try {
        return JSON.parse(o);
      } catch {
        return {};
      }
    return o ?? {};
  }
  function ht() {
    return window.currentSessionId ?? null;
  }
  function ie(t) {
    return typeof t == "string" ? t : t && typeof t == "object" && "text" in t ? t.text : String(t ?? "");
  }
  function Et(t) {
    if (t == null) return !0;
    const n = ie(t).trim();
    return !!(!n || /^[¥$]?0+(\.0+)?$/.test(n) || /^[-–—]+$/.test(n));
  }
  async function xt(t, n) {
    try {
      const o = U(), i = {
        "Content-Type": "application/json"
      };
      return o && (i.Authorization = `Bearer ${o}`), (await fetch(X("/interaction"), {
        method: "POST",
        headers: i,
        body: JSON.stringify({ session_id: t, result: n })
      })).ok;
    } catch {
      return !1;
    }
  }
  function Qe(t) {
    if (!t) return null;
    if (typeof t == "string")
      try {
        const n = JSON.parse(t);
        if (Array.isArray(n)) {
          const o = n.find(
            (i) => (i == null ? void 0 : i.type) === "text" && (i == null ? void 0 : i.text)
          );
          return (o == null ? void 0 : o.text) ?? null;
        }
        if (typeof n == "string") return n;
      } catch {
        return t;
      }
    if (Array.isArray(t)) {
      const n = t.find((o) => (o == null ? void 0 : o.type) === "text" && (o == null ? void 0 : o.text));
      return (n == null ? void 0 : n.text) ?? null;
    }
    return null;
  }
  function St(t) {
    var a, c;
    if (!t || t.length < 2) return null;
    const n = (c = (a = t[1]) == null ? void 0 : a.data) == null ? void 0 : c.output, o = Qe(n);
    if (!o) return null;
    if (o.startsWith("Error:")) return o;
    const i = o.match(/^用户选择了「(.+?)」并确认部署$/);
    if (i) return `已确认部署「${i[1]}」`;
    const d = o.match(
      /^用户选择「(.+?)」并要求调整[：:](.+)$/
    );
    if (d)
      return `已选择「${d[1]}」并调整：${d[2]}`;
    if (o === "用户确认部署") return "已确认部署";
    const g = o.match(/^用户要求调整资源[：:](.+)$/);
    return g ? `已反馈调整意见：${g[1]}` : "已确认";
  }
  const Ze = [
    "资源类型",
    "资源用途",
    "规格",
    "地域",
    "数量",
    "计费方式",
    "时长",
    "原价",
    "优惠",
    "预估算费用"
  ], wt = new Set(
    Ze.map((t) => t.toLowerCase())
  );
  function Le(t) {
    if (!Array.isArray(t) || t.length !== 10) return !1;
    const n = ie(t[0]).trim().toLowerCase();
    return wt.has(n);
  }
  function et(t) {
    if (!Array.isArray(t) || t.length !== 10) return !1;
    const n = ie(t[0]).trim();
    return /^(合计|总计|total)/i.test(n);
  }
  function At(t) {
    const n = [];
    let o = [];
    for (const i of t)
      o.push(i), et(i) && (n.push(o), o = []);
    return o.length > 0 && (n.length > 0 ? n[n.length - 1].push(...o) : n.push(o)), n.length > 0 ? n : [t];
  }
  function bt(t) {
    return typeof t == "string" ? t : t && typeof t == "object" && t.text ? t.url ? e.createElement(
      "a",
      {
        href: t.url,
        target: "_blank",
        rel: "noopener noreferrer"
      },
      t.text
    ) : t.text : String(t ?? "");
  }
  function kt({ data: t }) {
    var ge, m, b;
    const [n, o] = C("confirm"), [i, d] = C(""), [g, a] = C(!1), [c, s] = C(null), [I, A] = C(
      {}
    ), _ = e.useRef(!1), F = e.useRef(null), [, re] = C(0), L = t == null ? void 0 : t.content, B = L && L.length >= 2 && ((m = (ge = L[1]) == null ? void 0 : ge.data) == null ? void 0 : m.output), H = Ee(
      () => St(L),
      [L]
    ), z = _.current || B || H !== null, u = Ee(() => {
      const E = Ve(t), l = E == null ? void 0 : E.data;
      if (!l) return null;
      try {
        const y = typeof l == "string" ? JSON.parse(l) : l;
        let p;
        if (E.strategy_names)
          try {
            const P = typeof E.strategy_names == "string" ? JSON.parse(E.strategy_names) : E.strategy_names;
            p = Array.isArray(P) ? P : [];
          } catch {
            p = [];
          }
        else y != null && y.proposal_names ? p = y.proposal_names : p = [];
        const w = p.length >= 2 ? p.length : 0;
        let k;
        if (Array.isArray(y) && y.length > 0)
          if (Array.isArray(y[0]) && y[0].length === 10 && !Array.isArray(y[0][0])) {
            const D = y.filter(
              (se) => !Le(se)
            );
            if (D.filter(
              (se) => et(se)
            ).length >= 2)
              k = At(D);
            else if (w >= 2 && D.length >= w * 2) {
              const se = Math.ceil(D.length / w);
              k = [];
              for (let ye = 0; ye < D.length; ye += se)
                k.push(D.slice(ye, ye + se));
            } else
              k = [D];
          } else
            k = y.map(
              (D) => D.filter(
                (te) => Array.isArray(te) && te.length === 10 && !Le(te)
              )
            );
        else if (y != null && y.proposals)
          k = y.proposals.map(
            (P) => P.filter((D) => !Le(D))
          );
        else
          return null;
        if (k = k.filter((P) => P.length > 0), k.length === 0) return null;
        const de = ["方案一", "方案二", "方案三", "方案四", "方案五"];
        if (p.length < k.length)
          for (let P = p.length; P < k.length; P++)
            p.push(de[P] || `方案${P + 1}`);
        return { proposals: k, names: p };
      } catch {
        return null;
      }
    }, [t]), x = ht(), f = (((b = u == null ? void 0 : u.proposals) == null ? void 0 : b.length) ?? 0) > 1, O = R(async () => {
      if (!x || z || !u) return;
      const E = f ? c : 0, l = u.names[E ?? 0] || `方案${(E ?? 0) + 1}`;
      let y;
      n === "confirm" ? y = `用户选择了「${l}」并确认部署` : y = `用户选择「${l}」并要求调整：${i.trim() || "未填写具体要求"}`, a(!0);
      const p = await xt(x, y);
      a(!1), p ? (_.current = !0, n === "confirm" ? F.current = `已确认部署「${l}」` : F.current = `已选择「${l}」并调整：${i.trim()}`, re((w) => w + 1), qe.success(
        n === "confirm" ? "已确认部署方案" : "已提交调整意见"
      )) : qe.error("操作失败，请重试");
    }, [
      x,
      z,
      u,
      n,
      i,
      c,
      f
    ]), Ae = (t == null ? void 0 : t.status) === "in_progress" || (t == null ? void 0 : t.status) === "created";
    if (!u)
      return Ae ? e.createElement(
        "div",
        {
          style: {
            width: "100%",
            borderRadius: 10,
            border: "1px solid #f0f0f0",
            background: "#fff",
            padding: "24px 16px",
            margin: "4px 0",
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            gap: 12
          }
        },
        e.createElement(he, { size: "default" }),
        e.createElement(
          V,
          { type: "secondary", style: { fontSize: 13 } },
          "正在生成资源方案..."
        )
      ) : e.createElement(
        G,
        { size: "small", style: { margin: "4px 0" } },
        e.createElement(V, { type: "secondary" }, "无法解析方案数据")
      );
    const { proposals: ee, names: fe } = u, J = Ze.map((E, l) => ({
      title: E,
      dataIndex: `col_${l}`,
      key: `col_${l}`,
      render: (y) => bt(y),
      ellipsis: l < 3
    }));
    let me = "待确认", Q = "processing";
    z && (Q = "success", me = F.current || H || "已确认");
    const oe = e.createElement(
      $,
      {
        color: Q,
        style: { marginLeft: 4 }
      },
      me
    ), be = e.createElement(
      W,
      { size: 8 },
      e.createElement("span", null, "☁️"),
      e.createElement(
        V,
        { strong: !0, style: { fontSize: 14 } },
        z ? "资源配置方案" : "请确认您的资源配置方案"
      ),
      oe
    ), pe = ee.map((E, l) => {
      const y = f ? c === l : !0, p = I[l] || !1, w = (v) => {
        const ne = ie(v[0] || "").trim();
        return /^合计|^总计|^total/i.test(ne);
      }, k = E.find(w), de = E.filter((v) => !w(v)), P = de.map((v) => ({
        type: ie(v[0] || ""),
        purpose: ie(v[1] || ""),
        spec: ie(v[2] || ""),
        cost: v[9] ?? null
      })), D = k ? ie(k[9] ?? "") : "", te = E.map((v, ne) => {
        const Me = { key: ne };
        return v.forEach((_e, Fe) => {
          Me[`col_${Fe}`] = _e;
        }), Me;
      }), se = y ? "2px solid #1677ff" : "1px solid #e8e8e8", ye = y ? "0 0 0 2px #e6f4ff" : "none";
      return e.createElement(
        "div",
        {
          key: l,
          style: {
            flex: 1,
            minWidth: 240,
            border: se,
            borderRadius: 8,
            cursor: f ? "pointer" : "default",
            transition: "all 0.2s ease",
            boxShadow: ye,
            background: "#fff"
          },
          onClick: f ? () => s(l) : void 0
        },
        e.createElement(
          "div",
          { style: { padding: "10px 12px" } },
          // Proposal name
          e.createElement(
            V,
            {
              strong: !0,
              style: { fontSize: 14, display: "block", marginBottom: 8 }
            },
            fe[l]
          ),
          ...P.map(
            (v, ne) => e.createElement(
              "div",
              {
                key: ne,
                style: {
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                  padding: "4px 0",
                  borderBottom: ne < P.length - 1 ? "1px solid #f5f5f5" : "none"
                }
              },
              e.createElement(
                "div",
                { style: { flex: 1, minWidth: 0 } },
                e.createElement(
                  "span",
                  { style: { fontSize: 12, color: "#262626" } },
                  v.type
                ),
                v.spec && e.createElement(
                  "span",
                  {
                    style: { fontSize: 11, color: "#8c8c8c", marginLeft: 6 }
                  },
                  v.spec
                )
              ),
              !Et(v.cost) && e.createElement(
                "span",
                {
                  style: {
                    fontSize: 12,
                    color: "#595959",
                    flexShrink: 0,
                    marginLeft: 8
                  }
                },
                ie(v.cost)
              )
            )
          ),
          // Total cost
          D && e.createElement(
            "div",
            {
              style: {
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                marginTop: 6,
                paddingTop: 6,
                borderTop: "1px dashed #e8e8e8"
              }
            },
            e.createElement(
              "span",
              { style: { fontSize: 12, fontWeight: 500 } },
              "合计"
            ),
            e.createElement(
              "span",
              {
                style: { fontSize: 14, fontWeight: 700, color: "#fa541c" }
              },
              D
            )
          ),
          // Details toggle
          e.createElement(
            "div",
            {
              style: {
                display: "flex",
                alignItems: "center",
                gap: 4,
                color: "#8c8c8c",
                fontSize: 12,
                cursor: "pointer",
                marginTop: 6
              },
              onClick: (v) => {
                v.stopPropagation(), A((ne) => ({
                  ...ne,
                  [l]: !ne[l]
                }));
              }
            },
            e.createElement(
              p && Xe ? Xe : yt || "span",
              {
                style: { fontSize: 10 }
              }
            ),
            e.createElement(
              "span",
              null,
              `明细 · ${de.length} 项`
            )
          ),
          p && e.createElement(
            "div",
            {
              onClick: (v) => v.stopPropagation(),
              style: { marginTop: 4, maxHeight: 260, overflow: "auto" }
            },
            e.createElement(M, {
              columns: J,
              dataSource: te,
              pagination: !1,
              size: "small",
              scroll: { x: "max-content" }
            })
          )
        )
      );
    }), ae = e.createElement(
      "div",
      {
        style: {
          background: "#fffbe6",
          border: "1px solid #ffe58f",
          borderRadius: 6,
          padding: "8px 12px",
          marginBottom: 10,
          display: "flex",
          alignItems: "flex-start",
          gap: 8
        }
      },
      ze ? e.createElement(ze, {
        style: {
          color: "#faad14",
          fontSize: 14,
          flexShrink: 0,
          marginTop: 1
        }
      }) : e.createElement("span", null, "⚠️"),
      e.createElement(
        "span",
        {
          style: { fontSize: 12, color: "#8c6e00", lineHeight: 1.5 }
        },
        "在服务部署与配置过程中，可能因实际资源需求变化导致资源变配及费用调整，请及时关注实际资源使用情况与账单详情。"
      )
    ), xe = !z && x && !(f && c === null) && e.createElement(
      "div",
      null,
      e.createElement(
        "div",
        {
          style: {
            display: "flex",
            gap: 8,
            flexWrap: "wrap",
            marginBottom: 8
          }
        },
        // Confirm option
        e.createElement(
          "div",
          {
            style: {
              flex: 1,
              minWidth: 140,
              border: `1px solid ${n === "confirm" ? "#1677ff" : "#e8e8e8"}`,
              borderRadius: 6,
              padding: "8px 12px",
              cursor: "pointer",
              transition: "all 0.15s ease",
              display: "flex",
              alignItems: "center",
              gap: 8,
              background: n === "confirm" ? "#e6f4ff" : "transparent"
            },
            onClick: () => o("confirm")
          },
          e.createElement(ve, { checked: n === "confirm" }),
          e.createElement(
            "span",
            { style: { fontSize: 13 } },
            "确认部署"
          )
        ),
        // Adjust option
        e.createElement(
          "div",
          {
            style: {
              flex: 1,
              minWidth: 140,
              border: `1px solid ${n === "adjust" ? "#1677ff" : "#e8e8e8"}`,
              borderRadius: 6,
              padding: "8px 12px",
              transition: "all 0.15s ease",
              background: n === "adjust" ? "#e6f4ff" : "transparent"
            }
          },
          e.createElement(
            "div",
            {
              style: {
                display: "flex",
                alignItems: "center",
                gap: 8,
                cursor: "pointer"
              },
              onClick: () => o("adjust")
            },
            e.createElement(ve, { checked: n === "adjust" }),
            e.createElement(
              "span",
              { style: { fontSize: 13 } },
              "调整资源"
            )
          ),
          n === "adjust" && e.createElement(gt, {
            value: i,
            onChange: (E) => d(E.target.value),
            placeholder: "请输入调整要求",
            autoSize: { minRows: 1, maxRows: 3 },
            style: { fontSize: 12, marginTop: 6 }
          })
        )
      ),
      // Footer
      e.createElement(
        "div",
        {
          style: {
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            paddingTop: 8
          }
        },
        e.createElement(
          V,
          { type: "secondary", style: { fontSize: 11 } },
          f ? "一小时后未操作将自动选择第一个方案" : "一小时后未操作将自动确认部署"
        ),
        e.createElement(
          T,
          {
            type: "primary",
            size: "small",
            loading: g,
            onClick: O,
            disabled: n === "adjust" && !i.trim()
          },
          n === "confirm" ? "确认部署" : "提交调整"
        )
      )
    ), N = f && c === null && !z && e.createElement(
      "div",
      {
        style: {
          textAlign: "center",
          padding: "8px 0 4px",
          color: "rgba(0,0,0,0.45)",
          fontSize: 12
        }
      },
      "请点击选择一个方案后继续操作"
    );
    return e.createElement(
      "div",
      {
        style: {
          width: "100%",
          borderRadius: 10,
          border: "1px solid #f0f0f0",
          overflow: "hidden",
          background: "#fff",
          padding: "12px 16px",
          margin: "4px 0"
        }
      },
      // Header
      e.createElement("div", { style: { marginBottom: 10 } }, be),
      // Proposals grid
      e.createElement(
        "div",
        {
          style: {
            display: "flex",
            gap: 10,
            marginBottom: 12,
            flexWrap: "wrap"
          }
        },
        ...pe
      ),
      N,
      ae,
      !z && xe
    );
  }
  function Ct({ data: t }) {
    const [n, o] = C(null), [i, d] = C(!1), g = (t == null ? void 0 : t.status) === "in_progress" || (t == null ? void 0 : t.status) === "created", a = Ee(() => {
      const u = Ve(t);
      return (u == null ? void 0 : u.loop_dir) || null;
    }, [t]), c = Ee(() => {
      var x, f, O;
      const u = Qe((O = (f = (x = t == null ? void 0 : t.content) == null ? void 0 : x[1]) == null ? void 0 : f.data) == null ? void 0 : O.output);
      if (!u) return null;
      try {
        return JSON.parse(u);
      } catch {
        return null;
      }
    }, [t]), s = (c == null ? void 0 : c.status) === "ok", I = (c == null ? void 0 : c.status) === "error", A = I ? (c == null ? void 0 : c.message) || "未知错误" : null, _ = R(async () => {
      if (a)
        try {
          const u = U(), x = {};
          u && (x.Authorization = `Bearer ${u}`);
          const f = await fetch(
            X(`/prd?loop_dir=${encodeURIComponent(a)}`),
            { headers: x }
          );
          if (!f.ok) {
            d(!0);
            return;
          }
          const O = await f.json();
          O && Array.isArray(O.userStories) ? (o(O), d(!1)) : d(!0);
        } catch {
          d(!0);
        }
    }, [a]);
    if (e.useEffect(() => {
      !g && s && a && _();
    }, [g, s, a, _]), g)
      return e.createElement(
        "div",
        {
          style: {
            width: "100%",
            borderRadius: 10,
            border: "1px solid #f0f0f0",
            background: "#fff",
            padding: "24px 16px",
            margin: "4px 0",
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            gap: 12
          }
        },
        e.createElement(he, { size: "default" }),
        e.createElement(
          V,
          { type: "secondary", style: { fontSize: 13 } },
          "正在更新 PRD..."
        )
      );
    if (I)
      return e.createElement(
        "div",
        {
          style: {
            width: "100%",
            borderRadius: 10,
            border: "1px solid #fff1f0",
            background: "#fff1f0",
            padding: "12px 16px",
            margin: "4px 0",
            display: "flex",
            alignItems: "center",
            gap: 8
          }
        },
        e.createElement(
          V,
          { type: "danger", style: { fontSize: 13 } },
          `PRD 格式错误，将会修正：${A}`
        )
      );
    if (!s || i || !n) return null;
    const F = n.userStories, re = [...F].sort(
      (u, x) => (u.priority || 99) - (x.priority || 99)
    ), L = F.filter((u) => u.passes).length, B = [
      {
        title: "状态",
        key: "status",
        width: 50,
        align: "center",
        render: (u, x) => {
          if (x.passes) {
            const O = Oe ? e.createElement(Oe, {
              style: { color: "#52c41a", fontSize: 18 }
            }) : "✅";
            return e.createElement(Ke, { title: "已完成" }, O);
          }
          const f = Pe ? e.createElement(Pe, {
            style: { color: "#faad14", fontSize: 18 }
          }) : "🕐";
          return e.createElement(Ke, { title: "待处理" }, f);
        }
      },
      {
        title: "ID",
        dataIndex: "id",
        key: "id",
        width: 85,
        render: (u) => e.createElement($, { color: "blue" }, u)
      },
      {
        title: "标题",
        dataIndex: "title",
        key: "title",
        render: (u) => e.createElement(V, { strong: !0 }, u)
      },
      {
        title: "优先级",
        key: "priority",
        width: 70,
        render: (u, x) => {
          const f = x.priority;
          return e.createElement(
            $,
            { color: "default" },
            f != null ? String(f) : "-"
          );
        }
      },
      {
        title: "描述",
        dataIndex: "description",
        key: "description",
        ellipsis: !0
      },
      {
        title: "验收标准",
        key: "acceptance",
        width: 200,
        render: (u, x) => {
          const f = x.acceptanceCriteria;
          return typeof f == "string" ? e.createElement(
            "div",
            {
              style: { fontSize: 12, color: "#666", whiteSpace: "pre-wrap" }
            },
            f.length > 100 ? f.slice(0, 100) + "..." : f
          ) : Array.isArray(f) ? e.createElement(
            "div",
            { style: { fontSize: 12, color: "#666" } },
            f.length > 2 ? f.slice(0, 2).join(", ") + "..." : f.join(", ")
          ) : "-";
        }
      }
    ], H = e.createElement(
      W,
      { size: 8 },
      Ge ? e.createElement(Ge, { style: { color: "#1677ff" } }) : null,
      e.createElement(
        "span",
        { style: { fontSize: 14 } },
        e.createElement(V, { strong: !0 }, n.project || "PRD")
      )
    ), z = e.createElement(M, {
      columns: B,
      dataSource: re.map((u) => ({ ...u, key: u.id })),
      size: "small",
      pagination: !1,
      scroll: { x: "max-content" },
      style: { marginBottom: 4 }
    });
    return e.createElement(
      "div",
      {
        style: {
          width: "100%",
          borderRadius: 10,
          border: "1px solid #f0f0f0",
          overflow: "hidden",
          background: "#fff",
          padding: "12px 16px",
          margin: "4px 0"
        }
      },
      e.createElement("div", { style: { marginBottom: 8 } }, H),
      e.createElement(le, {
        size: "small",
        column: { xs: 1, sm: 2, md: 3 },
        style: { marginBottom: 12 },
        bordered: !1,
        items: [
          {
            key: "progress",
            label: "进度",
            children: `${L}/${F.length} 完成`
          }
        ]
      }),
      z,
      e.createElement(
        "div",
        {
          style: {
            fontSize: 11,
            color: "#8c8c8c",
            display: "flex",
            alignItems: "center",
            gap: 8
          }
        },
        Oe ? e.createElement(Oe, {
          style: { color: "#52c41a", fontSize: 14 }
        }) : "✅",
        e.createElement("span", null, "已完成"),
        e.createElement("span", { style: { margin: "0 4px" } }, "·"),
        Pe ? e.createElement(Pe, {
          style: { color: "#faad14", fontSize: 14 }
        }) : "🕐",
        e.createElement("span", null, "待处理")
      )
    );
  }
  const {
    Form: ce,
    Select: $e,
    Drawer: Tt,
    Modal: tt,
    Empty: vt,
    Badge: nt,
    Divider: It,
    message: K
  } = j, {
    ApiOutlined: rt,
    PlusOutlined: ot,
    ReloadOutlined: Ne,
    DeleteOutlined: at,
    LinkOutlined: st,
    DisconnectOutlined: Yt
  } = Y || {}, { useEffect: lt } = e, Se = "/a2a/agents", Be = {
    "阿里云Agent Hub": "Alibaba Cloud Agent Hub",
    ecs文件备份基础版助手: "Assistente de backup de arquivos ECS",
    ECS文件备份基础版助手: "Assistente de backup de arquivos ECS",
    "dataworks-基础设施管家": "DataWorks - gerenciador de infraestrutura",
    "DataWorks 基础设施管家": "DataWorks - gerenciador de infraestrutura",
    dataworks元数据助手: "Assistente de metadados DataWorks",
    DataWorks元数据助手: "Assistente de metadados DataWorks",
    ecs智能诊断助手: "Assistente de diagnóstico ECS",
    ECS智能诊断助手: "Assistente de diagnóstico ECS",
    阿里云elasticsearch实例管理助手: "Assistente de gerenciamento de instancias Elasticsearch",
    "emr-spark智能管理助手": "Assistente de gerenciamento EMR Spark",
    pts压测运维助手: "Assistente de operacao de testes de carga PTS",
    智能: "",
    基础设施: "infraestrutura",
    元数据: "metadados",
    助手: "assistente",
    管家: "gerenciador",
    文件备份: "backup de arquivos",
    诊断: "diagnostico",
    实例管理: "gerenciamento de instancias",
    压测运维: "operacao de testes de carga",
    未连接: "Nao conectado",
    已连接: "Conectado",
    错误: "Erro"
  };
  function q(t) {
    if (t == null) return "";
    let n = String(t);
    return Be[n] ? Be[n] : (Object.entries(Be).forEach(([o, i]) => {
      n = n.split(o).join(i);
    }), n);
  }
  function it(t) {
    return t;
  }
  function De() {
    var t;
    try {
      const n = sessionStorage.getItem("qwenpaw-agent-storage") || localStorage.getItem("qwenpaw-agent-storage");
      if (n) {
        const o = JSON.parse(n);
        return ((t = o == null ? void 0 : o.state) == null ? void 0 : t.selectedAgent) || null;
      }
    } catch {
    }
    return null;
  }
  async function we(t, n) {
    const o = X(t), i = U == null ? void 0 : U(), d = De(), g = {
      "Content-Type": "application/json",
      ...i ? { Authorization: `Bearer ${i}` } : {},
      ...d ? { "X-Agent-Id": d } : {}
    }, a = await fetch(o, {
      ...n,
      headers: { ...g, ...(n == null ? void 0 : n.headers) || {} }
    });
    if (!a.ok) {
      const c = await a.text().catch(() => "");
      throw new Error(c || `HTTP ${a.status}`);
    }
    return a.status === 204 || a.headers.get("content-length") === "0" ? null : a.json();
  }
  function _t(t) {
    var c;
    const { agent: n, onClick: o } = t, i = n.status === "connected", d = i ? "#52c41a" : n.status === "error" ? "#ff4d4f" : "#d9d9d9", g = i ? "Conectado" : n.status === "error" ? "Erro" : "Nao conectado", a = {
      gateway: "Alibaba Cloud Agent Hub",
      bearer: "Bearer Token",
      api_key: "API Key"
    };
    return e.createElement(
      G,
      {
        hoverable: !0,
        onClick: o,
        size: "small",
        style: { cursor: "pointer" },
        title: e.createElement(
          W,
          null,
          e.createElement(nt, { color: d }),
          e.createElement(
            "span",
            null,
            q(n.alias || n.name || n.url)
          )
        ),
        extra: n.auth_type ? e.createElement(
          $,
          { color: "blue" },
          a[n.auth_type] || n.auth_type
        ) : null
      },
      e.createElement(
        "div",
        { style: { fontSize: 12, color: "#666" } },
        e.createElement(
          "div",
          { style: { marginBottom: 4 } },
          st ? e.createElement(st, { style: { marginRight: 4 } }) : null,
          n.url
        ),
        n.description ? e.createElement(
          "div",
          { style: { marginBottom: 4, color: "#999" } },
          q(n.description)
        ) : null,
        ((c = n.skills) == null ? void 0 : c.length) > 0 ? e.createElement(
          "div",
          null,
          n.skills.slice(0, 3).map(
            (s, I) => e.createElement(
              $,
              { key: I, style: { fontSize: 11 } },
              q(s.name)
            )
          ),
          n.skills.length > 3 ? e.createElement(
            $,
            { style: { fontSize: 11 } },
            `+${n.skills.length - 3}`
          ) : null
        ) : null,
        e.createElement(
          "div",
          { style: { marginTop: 4, color: d, fontSize: 11 } },
          g,
          n.error ? ` - ${n.error}` : ""
        )
      )
    );
  }
  function Rt() {
    const t = e.useRef(De()), [n, o] = C(t.current);
    return lt(() => {
      const i = () => {
        const g = De();
        g !== t.current && (t.current = g, o(g));
      }, d = setInterval(i, 200);
      return window.addEventListener("storage", i), () => {
        clearInterval(d), window.removeEventListener("storage", i);
      };
    }, []), n;
  }
  function zt() {
    var mt, pt;
    const { token: t } = Ye.useToken(), n = Rt(), [o, i] = C([]), [d, g] = C(!0), [a, c] = C(!1), [s, I] = C(null), [A, _] = C(!1), [F, re] = C(!1), [L, B] = C(!1), [H, z] = C(!1), [u, x] = C(""), [f] = ce.useForm(), [O, Ae] = C(!1), [ee, fe] = C(!1), [J, me] = C([]), [Q, oe] = C(
      /* @__PURE__ */ new Set()
    ), [be, pe] = C(
      []
    ), ae = e.useRef(null), xe = (r) => !r || !r.trim() ? null : /\s/.test(r) ? "O apelido nao pode conter espacos" : null, N = Ee(
      () => new Set(o.map((r) => r.url)),
      [o]
    ), ge = e.useRef(N);
    ge.current = N;
    const m = R(async () => {
      g(!0);
      try {
        const r = await we(Se);
        i(((r == null ? void 0 : r.agents) || []).map(it));
      } catch {
        i([]);
      } finally {
        g(!1);
      }
    }, []);
    lt(() => {
      m();
    }, [n]);
    const b = R(() => {
      _(!0), I(null), c(!0), f.resetFields(), f.setFieldsValue({
        url: "",
        alias: "",
        auth_type: "",
        auth_token: ""
      });
    }, [f]), E = R((r) => {
      _(!1), I(r), c(!0);
    }, []), l = R(() => {
      z(!1), x("");
    }, []), y = R(async () => {
      if (!s || !u.trim()) return;
      const r = xe(u);
      if (r) {
        K.error(r);
        return;
      }
      const h = s.alias || s.url, S = u.trim();
      if (S === h) {
        l();
        return;
      }
      try {
        const ue = await we(
          `${Se}?alias=${encodeURIComponent(h)}`,
          {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ new_alias: S })
          }
        );
        K.success("Apelido alterado"), z(!1), I(ue), await m();
      } catch (ue) {
        K.error(ue.message || "Falha ao alterar");
      }
    }, [s, u, m, l]), p = R(() => {
      l(), c(!1), I(null), _(!1), f.resetFields();
    }, [l, f]), w = R(async () => {
      let r;
      try {
        r = await f.validateFields();
      } catch {
        return;
      }
      const h = {
        url: String(r.url || "").trim(),
        alias: String(r.alias || "").trim() || void 0,
        auth_type: String(r.auth_type || ""),
        auth_token: String(r.auth_token || "")
      };
      if (h.url) {
        re(!0);
        try {
          await we(Se, {
            method: "POST",
            body: JSON.stringify(h)
          }), K.success("A2A Agent registrado"), await m(), p();
        } catch (S) {
          K.error(S.message || "Falha ao registrar");
        } finally {
          re(!1);
        }
      }
    }, [f, m, p]), k = R(async () => {
      if (!s) return;
      const r = s.alias || s.url, h = q(s.name || r);
      tt.confirm({
        title: "Confirmar exclusao",
        content: `Excluir o A2A Agent "${h}"? Esta acao nao pode ser desfeita.`,
        okText: "Excluir",
        cancelText: "Cancelar",
        okButtonProps: { danger: !0 },
        async onOk() {
          try {
            await we(`${Se}?alias=${encodeURIComponent(r)}`, {
              method: "DELETE"
            }), K.success(`A2A Agent "${h}" excluido`), await m(), p();
          } catch (S) {
            K.error(S.message || "Falha ao excluir");
          }
        }
      });
    }, [s, m, p]), de = R(async () => {
      if (!s) return;
      const r = s.alias || s.url;
      B(!0);
      try {
        const h = await we(
          `${Se}/refresh?alias=${encodeURIComponent(r)}`,
          {
            method: "POST"
          }
        );
        K.success("Cartao do Agent atualizado"), await m(), h && I(h);
      } catch (h) {
        K.error(h.message || "Falha ao atualizar");
      } finally {
        B(!1);
      }
    }, [s, m]), P = R(() => {
      s && (x(s.alias || ""), z(!0));
    }, [s]), D = R(() => {
      Ae(!0), me([]), oe(/* @__PURE__ */ new Set()), pe([]), ae.current = null, se();
    }, []), te = R(() => {
      ee && ae.current && ae.current.abort(), Ae(!1), me([]), oe(/* @__PURE__ */ new Set()), pe([]), ae.current = null;
    }, [ee]), se = R(async () => {
      fe(!0);
      const r = new AbortController();
      ae.current = r;
      try {
        const h = U == null ? void 0 : U(), S = De(), ue = {
          ...h ? { Authorization: `Bearer ${h}` } : {},
          ...S ? { "X-Agent-Id": S } : {}
        }, Ce = await fetch(X("/a2a/import"), {
          method: "GET",
          headers: ue,
          signal: r.signal
        });
        if (!Ce.ok) {
          const Re = await Ce.text().catch(() => "");
          throw new Error(Re || `HTTP ${Ce.status}`);
        }
        const Je = await Ce.json(), Ue = (Je == null ? void 0 : Je.agents) || [];
        if (Ue.length === 0) {
          K.warning("Nenhum Agent disponivel encontrado");
          return;
        }
        me(Ue.map(it));
        const Wt = ge.current;
        oe(
          new Set(
            Ue.filter((Re) => !Wt.has(Re.url)).map((Re) => Re.url)
          )
        );
      } catch (h) {
        if ((h == null ? void 0 : h.name) === "AbortError") return;
        K.error(h.message || "Falha ao obter lista de Agents");
      } finally {
        fe(!1), ae.current = null;
      }
    }, []), ye = R((r) => {
      oe((h) => {
        const S = new Set(h);
        return S.has(r) ? S.delete(r) : S.add(r), S;
      });
    }, []), v = R(() => {
      oe(
        new Set(
          J.filter((r) => !N.has(r.url)).map((r) => r.url)
        )
      );
    }, [J, N]), ne = R(() => {
      oe(/* @__PURE__ */ new Set());
    }, []), Me = R(async () => {
      const r = J.filter(
        (S) => Q.has(S.url) && !N.has(S.url)
      );
      if (r.length === 0) {
        K.warning("Selecione pelo menos um Agent");
        return;
      }
      fe(!0), pe([]);
      const h = [];
      for (const S of r) {
        try {
          await we(Se, {
            method: "POST",
            body: JSON.stringify({
              url: S.url,
              alias: S.name || void 0,
              auth_type: S.auth_type || "gateway",
              auth_token: ""
            })
          }), h.push({ name: S.name || S.url, success: !0 });
        } catch (ue) {
          h.push({
            name: q(S.name || S.url),
            success: !1,
            error: ue.message || "Falha ao registrar"
          });
        }
        pe([...h]);
      }
      await m(), K.success(
        `Importacao concluida: ${h.filter((S) => S.success).length} sucesso(s), ${h.filter((S) => !S.success).length} falha(s)`
      ), fe(!1), setTimeout(() => te(), 800);
    }, [J, Q, m, N]), _e = ((mt = ce.useWatch) == null ? void 0 : mt.call(ce, "auth_type", f)) ?? "", Fe = e.createElement(
      ce,
      { form: f, layout: "vertical" },
      e.createElement(
        ce.Item,
        {
          name: "url",
          label: "Agent URL",
          rules: [{ required: !0, message: "Informe a URL do Agent" }]
        },
        e.createElement(Z, {
          placeholder: "https://agent.example.com"
        })
      ),
      e.createElement(
        ce.Item,
        {
          name: "alias",
          label: "Apelido",
          rules: [
            {
              validator: (r, h) => {
                const S = xe(h);
                return S ? Promise.reject(new Error(S)) : Promise.resolve();
              }
            }
          ]
        },
        e.createElement(Z, {
          placeholder: "Informe um apelido opcional"
        })
      ),
      e.createElement(
        ce.Item,
        { name: "auth_type", label: "Tipo de autenticacao" },
        e.createElement(
          $e,
          { allowClear: !0, placeholder: "Sem autenticacao" },
          e.createElement(
            $e.Option,
            { value: "bearer" },
            "Bearer Token"
          ),
          e.createElement($e.Option, { value: "api_key" }, "API Key"),
          e.createElement(
            $e.Option,
            { value: "gateway" },
            "Alibaba Cloud Agent Hub"
          )
        )
      ),
      _e === "gateway" ? e.createElement(
        "div",
        {
          style: {
            marginBottom: 16,
            padding: "8px 12px",
            background: "#f6ffed",
            border: "1px solid #b7eb8f",
            borderRadius: 6,
            fontSize: 12,
            color: "#52c41a"
          }
        },
        "O modo Alibaba Cloud Agent Hub usa automaticamente o AK-SK das variaveis de ambiente para obter um Bearer Token"
      ) : null,
      _e && _e !== "gateway" ? e.createElement(
        ce.Item,
        { name: "auth_token", label: "Credencial de autenticacao" },
        e.createElement(Z.Password, {
          placeholder: "Bearer Token 或 API Key"
        })
      ) : null
    ), Mt = s ? e.createElement(
      "div",
      null,
      e.createElement(
        le,
        { column: 1, bordered: !0, size: "small" },
        e.createElement(
          le.Item,
          { label: "URL" },
          s.url
        ),
        e.createElement(
          le.Item,
          { label: "Apelido" },
          H ? e.createElement(
            "div",
            {
              style: { display: "flex", alignItems: "center", gap: 6 }
            },
            e.createElement(Z, {
              value: u,
              onChange: (r) => x(r.target.value),
              onPressEnter: y,
              autoFocus: !0,
              placeholder: "Informe novo apelido",
              size: "small",
              style: { flex: 1 }
            }),
            e.createElement(
              T,
              {
                type: "link",
                size: "small",
                onClick: y,
                disabled: !u.trim(),
                style: { padding: 0 }
              },
              "Salvar"
            )
          ) : e.createElement(
            "div",
            {
              style: { display: "flex", alignItems: "center", gap: 8 }
            },
            e.createElement("span", null, s.alias || "-"),
            e.createElement(
              "a",
              {
                style: { fontSize: 12 },
                onClick: P
              },
              "Alterar"
            )
          )
        ),
        e.createElement(
          le.Item,
          { label: "Nome do Agent" },
          q(s.name) || "-"
        ),
        e.createElement(
          le.Item,
          { label: "Status" },
          e.createElement(nt, {
            color: s.status === "connected" ? "#52c41a" : s.status === "error" ? "#ff4d4f" : "#d9d9d9",
            text: s.status === "connected" ? "Conectado" : s.status === "error" ? "Erro" : "Nao conectado"
          })
        ),
        e.createElement(
          le.Item,
          { label: "Tipo de autenticacao" },
          s.auth_type ? e.createElement(
            $,
            { color: "blue" },
            {
              gateway: "Alibaba Cloud Agent Hub",
              bearer: "Bearer Token",
              api_key: "API Key"
            }[s.auth_type] || s.auth_type
          ) : "Sem autenticacao"
        ),
        e.createElement(
          le.Item,
          { label: "Descricao" },
          q(s.description) || "-"
        ),
        e.createElement(
          le.Item,
          { label: "Versao" },
          s.version || "-"
        )
      ),
      ((pt = s.skills) == null ? void 0 : pt.length) > 0 ? e.createElement(
        "div",
        { style: { marginTop: 16 } },
        e.createElement("h4", null, "Skills"),
        ...s.skills.map(
          (r, h) => e.createElement(
            G,
            { key: h, size: "small", style: { marginBottom: 8 } },
            e.createElement(
              "strong",
              null,
              q(r.name)
            ),
            r.description ? e.createElement(
              "div",
              { style: { color: "#666", fontSize: 12 } },
              q(r.description)
            ) : null
          )
        )
      ) : null,
      s.capabilities ? e.createElement(
        "div",
        { style: { marginTop: 16 } },
        e.createElement("h4", null, "Capacidades"),
        e.createElement(
          W,
          null,
          e.createElement(
            $,
            {
              color: s.capabilities.streaming ? "green" : "default"
            },
            "Streaming"
          ),
          e.createElement(
            $,
            {
              color: s.capabilities.push_notifications ? "green" : "default"
            },
            "Push Notifications"
          )
        )
      ) : null,
      s.error ? e.createElement(
        "div",
        {
          style: {
            marginTop: 16,
            padding: "8px 12px",
            background: "#fff2f0",
            border: "1px solid #ffccc7",
            borderRadius: 6,
            fontSize: 12,
            color: "#ff4d4f"
          }
        },
        s.error
      ) : null,
      e.createElement(It, null),
      e.createElement(
        W,
        null,
        e.createElement(
          T,
          {
            type: "primary",
            icon: Ne ? e.createElement(Ne) : null,
            loading: L,
            onClick: de
          },
          "Atualizar cartao do Agent"
        ),
        e.createElement(
          T,
          {
            danger: !0,
            icon: at ? e.createElement(at) : null,
            onClick: k
          },
          "Excluir"
        )
      )
    ) : null, Lt = e.createElement(
      Tt,
      {
        title: A ? "Registrar A2A Agent remoto" : q((s == null ? void 0 : s.name) || (s == null ? void 0 : s.alias)) || "Detalhes do Agent",
        open: a,
        onClose: p,
        width: 480,
        footer: A ? e.createElement(
          W,
          { style: { display: "flex", justifyContent: "flex-end" } },
          e.createElement(T, { onClick: p }, "Cancelar"),
          e.createElement(
            T,
            { type: "primary", loading: F, onClick: w },
            "Registrar"
          )
        ) : null
      },
      A ? Fe : Mt
    ), Bt = e.createElement(
      "div",
      { style: { marginBottom: 16 } },
      e.createElement(
        "div",
        {
          style: {
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center"
          }
        },
        e.createElement(
          "h2",
          { style: { margin: 0 } },
          "A2A Agents remotos"
        ),
        e.createElement(
          W,
          null,
          e.createElement(
            T,
            {
              icon: Ne ? e.createElement(Ne) : null,
              onClick: m,
              loading: d
            },
            "Atualizar lista"
          ),
          e.createElement(
            T,
            {
              icon: rt ? e.createElement(rt) : null,
              onClick: D
            },
            "Importar do Alibaba Cloud Agent Hub"
          ),
          e.createElement(
            T,
            {
              type: "primary",
              icon: ot ? e.createElement(ot) : null,
              onClick: b
            },
            "Registrar Agent"
          )
        )
      ),
      e.createElement(
        "div",
        {
          style: {
            marginTop: 8,
            fontSize: 12,
            color: "#8c8c8c",
            lineHeight: 1.6
          }
        },
        ze ? e.createElement(ze, {
          style: { marginRight: 4, color: "#faad14" }
        }) : null,
        "No momento, o A2A conecta pelo CloudPaw aos Agents do portal Alibaba Cloud Skills. Outros Agents podem ter incompatibilidades."
      )
    ), Ht = d ? e.createElement(
      "div",
      { style: { textAlign: "center", padding: 60 } },
      e.createElement(he, { size: "large" })
    ) : o.length === 0 ? e.createElement(vt, {
      description: "Nenhum A2A Agent remoto registrado"
    }) : e.createElement(
      "div",
      {
        style: {
          display: "grid",
          gridTemplateColumns: "repeat(auto-fill, minmax(340px, 1fr))",
          gap: 12
        }
      },
      ...o.map(
        (r) => e.createElement(_t, {
          key: r.alias || r.url,
          agent: r,
          onClick: () => E(r)
        })
      )
    ), ke = be.length > 0, jt = e.createElement(
      tt,
      {
        title: ke ? "Resultado da importacao" : "Importar Agent do Alibaba Cloud Agent Hub",
        open: O,
        onCancel: te,
        closable: !ee || ke,
        maskClosable: !ee || ke,
        width: 800,
        footer: ke ? e.createElement(
          W,
          { style: { display: "flex", justifyContent: "flex-end" } },
          e.createElement(
            T,
            { type: "primary", onClick: te },
            "Fechar"
          )
        ) : J.length > 0 ? e.createElement(
          W,
          { style: { display: "flex", justifyContent: "flex-end" } },
          e.createElement(
            T,
            { onClick: te },
            "Cancelar"
          ),
          e.createElement(
            T,
            {
              type: "primary",
              loading: ee,
              disabled: Q.size === 0,
              onClick: Me
            },
            `Confirmar importacao (${Q.size}/${J.length})`
          )
        ) : null
      },
      // Loading state
      ee && J.length === 0 && e.createElement(
        "div",
        {
          style: {
            textAlign: "center",
            padding: 40,
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            gap: 12
          }
        },
        e.createElement(he, { size: "large" }),
        e.createElement(
          "span",
          { style: { fontSize: 13, color: t.colorTextTertiary } },
          "Obtendo lista de Agents do Agent Hub..."
        )
      ),
      // Agent selection list (hide after import completed)
      !ee && !ke && J.length > 0 && e.createElement(
        "div",
        null,
        // Header bar
        e.createElement(
          "div",
          {
            style: {
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
              marginBottom: 8,
              fontSize: 12,
              color: t.colorTextTertiary
            }
          },
          e.createElement(
            "span",
            null,
            `${J.length} Agents, ${Q.size} selecionado(s)`
          ),
          e.createElement(
            W,
            { size: 4 },
            e.createElement(
              T,
              {
                size: "small",
                type: "link",
                style: { padding: 0, height: "auto" },
                onClick: v
              },
              "Selecionar todos"
            ),
            e.createElement(
              T,
              {
                size: "small",
                type: "link",
                style: { padding: 0, height: "auto" },
                onClick: ne
              },
              "Limpar selecao"
            )
          )
        ),
        // Agent list
        e.createElement(
          "div",
          {
            style: {
              display: "flex",
              flexDirection: "column",
              gap: 8,
              maxHeight: 420,
              overflowY: "auto"
            }
          },
          ...J.map((r) => {
            var S;
            const h = Q.has(r.url);
            return e.createElement(
              "div",
              {
                key: r.url,
                style: {
                  display: "flex",
                  gap: 8,
                  padding: 10,
                  border: h ? `1px solid ${t.colorInfo}` : `1px solid ${t.colorBorderSecondary}`,
                  borderRadius: 6,
                  cursor: N.has(r.url) ? "default" : "pointer",
                  background: N.has(r.url) ? t.colorBgLayout : h ? t.colorInfoBg : t.colorBgContainer,
                  transition: "all 0.15s ease",
                  opacity: N.has(r.url) ? 0.7 : 1
                },
                onClick: () => {
                  N.has(r.url) || ye(r.url);
                }
              },
              e.createElement(
                "div",
                { style: { flex: 1, minWidth: 0 } },
                e.createElement(
                  "div",
                  {
                    style: {
                      fontWeight: 500,
                      fontSize: 13,
                      marginBottom: 2
                    }
                  },
                  q(r.name || r.url)
                ),
                r.description ? e.createElement(
                  "div",
                  {
                    style: {
                      fontSize: 11,
                      color: t.colorTextTertiary,
                      overflow: "hidden",
                      textOverflow: "ellipsis",
                      whiteSpace: "nowrap"
                    }
                  },
                  q(r.description)
                ) : null,
                ((S = r.skills) == null ? void 0 : S.length) > 0 ? e.createElement(
                  "div",
                  { style: { marginTop: 4 } },
                  ...r.skills.slice(0, 3).map(
                    (ue, Ce) => e.createElement(
                      $,
                      {
                        key: Ce,
                        color: t.colorInfoHover,
                        style: {
                          fontSize: 10,
                          marginRight: 4,
                          fontWeight: 500
                        }
                      },
                      q(ue.name)
                    )
                  ),
                  r.skills.length > 3 ? e.createElement(
                    $,
                    { style: { fontSize: 10 } },
                    `+${r.skills.length - 3}`
                  ) : null
                ) : null
              ),
              N.has(r.url) ? e.createElement(
                $,
                {
                  color: t.colorSuccess,
                  style: {
                    fontWeight: 600,
                    fontSize: 11,
                    flexShrink: 0,
                    padding: "2px 8px",
                    lineHeight: "18px",
                    height: 22,
                    borderRadius: 4
                  }
                },
                "Importado"
              ) : null
            );
          })
        )
      ),
      // Import results
      ke && e.createElement(
        "div",
        {
          style: {
            maxHeight: 350,
            overflowY: "auto",
            display: "flex",
            flexDirection: "column",
            gap: 6
          }
        },
        ...be.map(
          (r, h) => e.createElement(
            "div",
            {
              key: h,
              style: {
                display: "flex",
                alignItems: "center",
                gap: 8,
                padding: "6px 10px",
                borderRadius: 4,
                background: r.success ? t.colorInfoBg : t.colorErrorBg,
                border: r.success ? `1px solid ${t.colorInfo}` : `1px solid ${t.colorErrorBorder}`,
                fontSize: 12
              }
            },
            e.createElement(
              "span",
              {
                style: {
                  color: r.success ? t.colorSuccess : t.colorError,
                  fontSize: 14
                }
              },
              r.success ? "✓" : "✗"
            ),
            e.createElement(
              "span",
              {
                style: {
                  flex: 1,
                  color: r.success ? t.colorText : t.colorError
                }
              },
              r.name,
              r.error ? ` - ${r.error}` : ""
            )
          )
        )
      )
    );
    return e.createElement(
      "div",
      { style: { padding: 24 } },
      Bt,
      Ht,
      Lt,
      jt
    );
  }
  function Ot({ data: t }) {
    var xe, N, ge;
    const { token: n } = Ye.useToken(), o = e.useRef(null), [i, d] = C({}), g = Ee(() => {
      var b, E, l;
      const m = (l = (E = (b = t == null ? void 0 : t.content) == null ? void 0 : b[0]) == null ? void 0 : E.data) == null ? void 0 : l.arguments;
      if (!m) return null;
      try {
        return JSON.parse(m);
      } catch {
        return null;
      }
    }, [(ge = (N = (xe = t == null ? void 0 : t.content) == null ? void 0 : xe[0]) == null ? void 0 : N.data) == null ? void 0 : ge.arguments]), { toolResult: a, rawErrorText: c } = Ee(() => {
      var b;
      const m = t == null ? void 0 : t.content;
      if (!Array.isArray(m))
        return { toolResult: null, rawErrorText: "" };
      for (const E of m) {
        const l = (b = E == null ? void 0 : E.data) == null ? void 0 : b.output;
        if (!l) continue;
        let y = "";
        if (Array.isArray(l)) {
          const p = l.find(
            (w) => (w == null ? void 0 : w.type) === "text" && (w == null ? void 0 : w.text)
          );
          y = (p == null ? void 0 : p.text) || "";
        } else if (typeof l == "string")
          try {
            const p = JSON.parse(l);
            if (typeof p == "object" && (p != null && p.steps || p != null && p.response_text))
              return { toolResult: p, rawErrorText: "" };
            if (Array.isArray(p)) {
              const w = p.find((k) => (k == null ? void 0 : k.type) === "text" && (k == null ? void 0 : k.text));
              w != null && w.text && (y = w.text);
            }
          } catch {
            y = l;
          }
        if (y)
          try {
            return { toolResult: JSON.parse(y), rawErrorText: "" };
          } catch {
            return { toolResult: null, rawErrorText: y };
          }
      }
      return { toolResult: null, rawErrorText: "" };
    }, [t == null ? void 0 : t.content]), s = (a == null ? void 0 : a.steps) || [], I = (a == null ? void 0 : a.task_state) || "", A = (a == null ? void 0 : a.error) || "", _ = (a == null ? void 0 : a.response_text) || "", F = (a == null ? void 0 : a.context_id) || "";
    e.useEffect(() => {
      o.current && (o.current.scrollTop = o.current.scrollHeight);
    }, [s.length, _, c]), e.useEffect(() => {
      const m = { ...i };
      let b = !1;
      s.forEach((E, l) => {
        i[l] === void 0 && (E.type === "thinking" && E.done || E.type === "tool_call" && E.status !== "running") && (m[l] = !0, b = !0);
      }), b && d(m);
    }, [s]);
    const re = (g == null ? void 0 : g.agent_alias) || "", L = (g == null ? void 0 : g.agent_url) || "", B = re || L || "远程 Agent", H = {
      completed: { color: "#52c41a", text: "已完成" },
      TASK_STATE_COMPLETED: { color: "#52c41a", text: "已完成" },
      failed: { color: "#ff4d4f", text: "失败" },
      TASK_STATE_FAILED: { color: "#ff4d4f", text: "失败" },
      error: { color: "#ff4d4f", text: "出错" },
      canceled: { color: "#faad14", text: "已取消" },
      TASK_STATE_CANCELED: { color: "#faad14", text: "已取消" },
      AWAITING_USER_INPUT: { color: "#1677ff", text: "等待输入" },
      input_required: { color: "#1677ff", text: "等待输入" }
    }, x = (a !== null || !!c) && !(I === "working" || I === "TASK_STATE_WORKING");
    let f = "#1677ff", O = "执行中...";
    x && (H[I] ? (f = H[I].color, O = H[I].text) : c ? (f = "#ff4d4f", O = "出错") : (f = "#52c41a", O = "已完成"));
    const Ae = e.createElement(
      W,
      { size: 6 },
      e.createElement("span", { style: { fontSize: 13 } }, "🔗"),
      e.createElement(
        V,
        { style: { fontSize: 12, color: "#595959" } },
        `A2A: ${B}`
      ),
      e.createElement(
        $,
        { color: f, style: { fontSize: 11, lineHeight: "18px" } },
        O
      )
    ), ee = F ? e.createElement(
      "div",
      {
        style: {
          fontSize: 10,
          fontFamily: "monospace",
          maxWidth: "100%",
          overflow: "hidden",
          textOverflow: "ellipsis",
          whiteSpace: "nowrap",
          lineHeight: "16px",
          padding: "2px 8px",
          borderRadius: 4,
          marginBottom: 6,
          background: n.colorBgLayout,
          color: n.colorTextSecondary
        }
      },
      `contextId: ${F}`
    ) : null, fe = [Ae, ee], J = s.length === 0 && !c && !A, me = !x && J ? e.createElement(
      "div",
      {
        style: {
          display: "flex",
          alignItems: "center",
          gap: 8,
          padding: "6px 10px",
          marginBottom: 8,
          background: "#f6ffed",
          border: "1px solid #b7eb8f",
          borderRadius: 6
        }
      },
      e.createElement(he, { size: "small" }),
      e.createElement(
        V,
        { style: { fontSize: 12, color: "#52c41a" } },
        `正在连接 ${B}...`
      )
    ) : null;
    function Q(m) {
      d((b) => ({
        ...b,
        [m]: !b[m]
      }));
    }
    function oe(m, b) {
      const E = !!i[b];
      if (m.type === "thinking") {
        const l = !!m.done, y = l ? "💭" : "🧠", p = l ? "思考完成" : "思考中...", w = e.createElement(
          "div",
          {
            key: `step-${b}`,
            style: {
              display: "flex",
              alignItems: "center",
              gap: 6,
              padding: "3px 0",
              cursor: l ? "pointer" : "default",
              fontSize: 12,
              color: "#8c8c8c"
            },
            onClick: l ? () => Q(b) : void 0
          },
          l && e.createElement(
            "span",
            { style: { fontSize: 10, color: "#bfbfbf" } },
            E ? "▶" : "▼"
          ),
          e.createElement("span", null, y),
          e.createElement("span", null, p),
          !l && e.createElement(he, {
            size: "small",
            style: { marginLeft: 4 }
          })
        );
        return E ? w : e.createElement(
          "div",
          { key: `step-${b}` },
          w,
          e.createElement(
            "div",
            {
              style: {
                marginLeft: 20,
                padding: "4px 8px",
                background: "#fafafa",
                borderRadius: 4,
                fontSize: 12,
                color: "#595959",
                whiteSpace: "pre-wrap",
                wordBreak: "break-word",
                maxHeight: 120,
                overflowY: "auto",
                lineHeight: "1.5"
              }
            },
            m.text || ""
          )
        );
      }
      if (m.type === "tool_call") {
        const l = m.status === "running", y = m.status === "error", p = l ? "⚙️" : y ? "❌" : "✅", w = l ? `正在执行: ${m.name}` : y ? `执行失败: ${m.name}` : `执行完成: ${m.name}`, k = l ? "#1677ff" : y ? "#ff4d4f" : "#52c41a", de = e.createElement(
          "div",
          {
            key: `step-${b}`,
            style: {
              display: "flex",
              alignItems: "center",
              gap: 6,
              padding: "3px 0",
              cursor: l ? "default" : "pointer",
              fontSize: 12,
              color: k
            },
            onClick: l ? void 0 : () => Q(b)
          },
          !l && e.createElement(
            "span",
            { style: { fontSize: 10, color: "#bfbfbf" } },
            E ? "▶" : "▼"
          ),
          e.createElement("span", null, p),
          e.createElement("span", null, w),
          l && e.createElement(he, {
            size: "small",
            style: { marginLeft: 4 }
          })
        );
        return E || !m.desc && !l ? de : e.createElement(
          "div",
          { key: `step-${b}` },
          de,
          m.desc && e.createElement(
            "div",
            {
              style: {
                marginLeft: 20,
                padding: "2px 8px",
                fontSize: 11,
                color: "#8c8c8c"
              }
            },
            m.desc
          )
        );
      }
      return m.type === "text" ? e.createElement(
        "div",
        {
          key: `step-${b}`,
          style: {
            padding: "4px 0",
            fontSize: 12,
            whiteSpace: "pre-wrap",
            wordBreak: "break-word",
            lineHeight: "1.6",
            color: "#262626"
          }
        },
        m.text || ""
      ) : null;
    }
    const be = s.length > 0 ? e.createElement(
      "div",
      {
        ref: o,
        style: {
          background: "#fafafa",
          border: "1px solid #e8e8e8",
          borderRadius: 6,
          padding: "6px 10px",
          maxHeight: 200,
          overflowY: "auto"
        }
      },
      ...s.map(oe)
    ) : null, pe = c || A ? e.createElement(
      "div",
      {
        style: {
          background: "#fff2f0",
          border: "1px solid #ffccc7",
          borderRadius: 6,
          padding: "8px 12px",
          fontSize: 12,
          color: "#ff4d4f",
          whiteSpace: "pre-wrap",
          wordBreak: "break-word"
        }
      },
      A ? `错误: ${A}` : c
    ) : null, ae = !s.length && _ && !c ? e.createElement(
      "div",
      {
        ref: o,
        style: {
          background: "#fafafa",
          border: "1px solid #e8e8e8",
          borderRadius: 6,
          padding: "10px 12px",
          maxHeight: 200,
          overflowY: "auto"
        }
      },
      e.createElement(
        V,
        {
          style: {
            fontSize: 12,
            whiteSpace: "pre-wrap",
            wordBreak: "break-word",
            lineHeight: "1.6"
          }
        },
        _
      )
    ) : null;
    return e.createElement(
      "div",
      {
        style: {
          width: "100%",
          borderRadius: 8,
          border: "1px solid #f0f0f0",
          overflow: "hidden",
          background: "#fff",
          padding: "8px 12px",
          margin: "4px 0"
        }
      },
      e.createElement(
        "div",
        { style: { marginBottom: 6 } },
        ...fe
      ),
      me,
      be,
      ae,
      pe
    );
  }
  const Pt = "__A2A_STREAM_START__", $t = "A2A_STREAM_START", Ie = /* @__PURE__ */ new Set();
  function He(t) {
    return t ? t.includes(Pt) || t.includes($t) : !1;
  }
  function je(t) {
    var n, o;
    return t.getAttribute("data-msg-id") || t.getAttribute("data-message-id") || ((n = t.closest("[data-msg-id]")) == null ? void 0 : n.getAttribute("data-msg-id")) || ((o = t.closest("[data-message-id]")) == null ? void 0 : o.getAttribute("data-message-id")) || null;
  }
  function Nt(t) {
    if (He(t.innerHTML) || He(t.textContent))
      return t;
    const n = document.createTreeWalker(
      t,
      NodeFilter.SHOW_ELEMENT | NodeFilter.SHOW_TEXT
    );
    for (; n.nextNode(); ) {
      const o = n.currentNode, i = o.nodeType === Node.TEXT_NODE ? o.textContent : o.innerHTML;
      if (He(i)) {
        const d = o.nodeType === Node.TEXT_NODE ? o.parentElement : o;
        if (d) return d;
      }
    }
    return null;
  }
  async function We(t) {
    var s, I;
    const n = window.QwenPaw;
    if (!(n != null && n.host)) {
      console.warn("[a2a] QwenPaw.host not available");
      return;
    }
    const { getApiUrl: o, getApiToken: i } = n.host, d = o("/a2a/call/stream"), g = i();
    console.log("[a2a] Subscribing to SSE stream:", d);
    const a = document.createElement("div");
    a.style.cssText = "background:#f6ffed;border:1px solid #b7eb8f;border-radius:8px;padding:12px 16px;margin:4px 0;font-size:13px;white-space:pre-wrap;word-break:break-word;color:#262626;min-height:24px;", a.textContent = "正在连接远程 Agent...", t.textContent = "", t.appendChild(a);
    const c = new AbortController();
    try {
      const A = {
        Accept: "text/event-stream"
      };
      g && (A.Authorization = `Bearer ${g}`);
      try {
        const B = sessionStorage.getItem("qwenpaw-agent-storage") || localStorage.getItem("qwenpaw-agent-storage"), H = (I = (s = JSON.parse(B || "{}")) == null ? void 0 : s.state) == null ? void 0 : I.selectedAgent;
        H && (A["X-Agent-Id"] = H);
      } catch {
      }
      console.log("[a2a] Fetching SSE with headers:", A);
      const _ = await fetch(d, { headers: A, signal: c.signal });
      if (console.log("[a2a] SSE response status:", _.status), !_.ok) {
        const B = await _.text().catch(() => "");
        a.textContent = `SSE 连接失败 (${_.status}): ${B.slice(
          0,
          100
        )}`, a.style.borderColor = "#ff4d4f", a.style.background = "#fff1f0";
        return;
      }
      if (!_.body) {
        a.textContent = "SSE 连接失败：无响应体", a.style.borderColor = "#ff4d4f", a.style.background = "#fff1f0";
        return;
      }
      const F = _.body.getReader(), re = new TextDecoder();
      let L = "";
      for (; ; ) {
        const { done: B, value: H } = await F.read();
        if (B) {
          console.log("[a2a] SSE stream ended (done)");
          break;
        }
        L += re.decode(H, { stream: !0 });
        const z = L.split(`
`);
        L = z.pop() || "";
        for (const u of z)
          if (u.startsWith("data: "))
            try {
              const x = JSON.parse(u.slice(6));
              if (console.log("[a2a] SSE event:", x), x.done) {
                x.error && (a.textContent = `错误: ${x.error}`, a.style.borderColor = "#ff4d4f", a.style.background = "#fff1f0"), console.log("[a2a] SSE done signal received");
                return;
              }
              typeof x.response_text == "string" && x.response_text && (a.textContent = x.response_text);
            } catch (x) {
              console.warn("[a2a] SSE parse error:", x, "line:", u);
            }
      }
    } catch (A) {
      (A == null ? void 0 : A.name) !== "AbortError" && (console.error("[a2a] SSE subscription error:", A), a.textContent = `连接出错: ${(A == null ? void 0 : A.message) || A}`, a.style.borderColor = "#ff4d4f", a.style.background = "#fff1f0");
    }
  }
  function Dt() {
    console.log("[a2a] Initializing stream interceptor");
    function t(d) {
      if (d.nodeType !== Node.ELEMENT_NODE) return;
      const g = d, a = je(g);
      if (a && Ie.has(a)) return;
      const c = Nt(g);
      c && (console.log("[a2a] Marker detected in DOM, msgId:", a), a && Ie.add(a), We(c));
    }
    new MutationObserver((d) => {
      for (const g of d) {
        for (const a of g.addedNodes)
          t(a);
        g.target.nodeType === Node.ELEMENT_NODE && t(g.target);
      }
    }).observe(document.body, {
      childList: !0,
      subtree: !0,
      characterData: !0,
      characterDataOldValue: !0
    });
    const o = setInterval(() => {
      const d = document.evaluate(
        "//text()[contains(., 'A2A_STREAM_START')]",
        document.body,
        null,
        XPathResult.ORDERED_NODE_SNAPSHOT_TYPE,
        null
      );
      for (let g = 0; g < d.snapshotLength; g++) {
        const c = d.snapshotItem(g).parentElement;
        if (c) {
          const s = je(c);
          if (s && Ie.has(s)) continue;
          console.log("[a2a] Marker found in periodic scan, msgId:", s), s && Ie.add(s), We(c);
        }
      }
    }, 500);
    window.addEventListener("beforeunload", () => clearInterval(o));
    const i = document.evaluate(
      "//text()[contains(., 'A2A_STREAM_START')]",
      document.body,
      null,
      XPathResult.ORDERED_NODE_SNAPSHOT_TYPE,
      null
    );
    for (let d = 0; d < i.snapshotLength; d++) {
      const a = i.snapshotItem(d).parentElement;
      if (a) {
        const c = je(a);
        c && Ie.add(c), console.log("[a2a] Marker found in existing DOM, msgId:", c), We(a);
      }
    }
  }
  (dt = (ct = window.QwenPaw).registerToolRender) == null || dt.call(ct, "cloudpaw", {
    proposal_choice: kt,
    manage_prd: Ct,
    a2a_call: Ot
  }), (ft = (ut = window.QwenPaw).registerRoutes) == null || ft.call(ut, "cloudpaw", [
    {
      path: "/a2a",
      component: zt,
      label: "A2A",
      icon: "🔗",
      priority: 10
    }
  ]), Jt(), Ut(), Dt();
}
function Jt() {
  const e = "qwenpaw-last-used-agent", j = "qwenpaw-agent-storage", Y = "cloudpaw-first-install", X = "cloud-orchestrator";
  if (localStorage.getItem(Y)) return;
  localStorage.setItem(Y, "true");
  function U() {
    localStorage.setItem(e, X);
    try {
      const G = localStorage.getItem(j);
      if (G) {
        const M = JSON.parse(G);
        M.state = M.state || {}, M.state.selectedAgent = X, localStorage.setItem(j, JSON.stringify(M));
      } else
        localStorage.setItem(
          j,
          JSON.stringify({
            version: 0,
            state: {
              selectedAgent: X,
              agents: [],
              lastChatIdByAgent: {}
            }
          })
        );
    } catch {
    }
    try {
      const G = sessionStorage.getItem(j);
      if (G) {
        const M = JSON.parse(G);
        M.state = M.state || {}, M.state.selectedAgent = X, sessionStorage.setItem(j, JSON.stringify(M));
      } else
        sessionStorage.setItem(
          j,
          JSON.stringify({
            version: 0,
            state: {
              selectedAgent: X,
              agents: [],
              lastChatIdByAgent: {}
            }
          })
        );
    } catch {
    }
  }
  U(), window.addEventListener(
    "beforeunload",
    () => {
      U();
    },
    { once: !0 }
  ), console.info(
    "[cloudpaw] Set default agent to cloud-orchestrator for first-time user"
  ), window.location.reload();
}
function Ut() {
  var W;
  const e = (W = window.QwenPaw) == null ? void 0 : W.modules;
  if (!e) return;
  const j = e["Chat/OptionsPanel/defaultConfig"];
  if (!(j != null && j.configProvider)) {
    console.warn(
      "[cloudpaw] configProvider not found — skipping welcome/theme patch"
    );
    return;
  }
  const Y = j.configProvider, X = Y.getConfig.bind(Y), U = "https://gw.alicdn.com/imgextra/i2/O1CN01pyXzjQ1EL1PuZMlSd_!!6000000000334-2-tps-288-288.png", G = {
    zh: "CloudPaw 插件提示",
    en: "CloudPaw Plugin Tips",
    ja: "CloudPaw プラグインのヒント",
    ru: "Подсказки плагина CloudPaw"
  }, M = {
    zh: `告诉 CloudPaw 你想做什么，它会自动帮你完成云资源管理、基础设施编排与应用创建上云等任务。
⚠️ 使用前请在左上角下拉框切换到「CloudPaw-Master」，否则功能无法正常使用！
对于复杂的长程任务，建议使用 /mission 命令启动 Mission Mode 来自动拆解和执行。`,
    en: `Tell CloudPaw what you want to do — it will automatically handle cloud resource management, infrastructure orchestration, and application deployment.
⚠️ Please switch to 'CloudPaw-Master' from the dropdown in the top-left corner before use — features won't work otherwise!
For complex, multi-step tasks, use /mission to start Mission Mode for automated decomposition and execution.`,
    ja: `CloudPaw にやりたいことを伝えるだけで、クラウドリソース管理、インフラ構成、アプリケーションのデプロイなどを自動で行います。
⚠️ 使用前に左上のドロップダウンから「CloudPaw-Master」に切り替えてください。切り替えないと機能が正常に動作しません！
複雑なタスクには /mission コマンドで Mission Mode を起動し、自動分解・実行できます。`,
    ru: `Расскажите CloudPaw, что вы хотите сделать — он автоматически выполнит управление облачными ресурсами, оркестрацию инфраструктуры и развёртывание приложений.
⚠️ Перед началом переключитесь на 'CloudPaw-Master' в выпадающем списке в левом верхнем углу — иначе функции не будут работать!
Для сложных задач используйте /mission для автоматической декомпозиции и выполнения.`
  }, $ = {
    zh: [
      {
        label: "创建个人主页并部署到云端",
        value: "/mission 帮我创建一个个人主页并上线到云端。页面包含：个人介绍、技能展示、项目经历、联系方式，所有个人信息请先用占位符代替。风格简洁清爽，适配手机和电脑。请使用阿里云 ECS 部署。"
      },
      {
        label: "快速发布 API 服务到云端",
        value: "/mission 帮我把一个 API 服务快速发布到云端。我希望默认提供 /health 和 /hello 两个接口，并给我可直接调用的地址和示例请求，配置尽量简单清晰。"
      }
    ],
    en: [
      {
        label: "Create a personal homepage and deploy to the cloud",
        value: "/mission Help me create a personal homepage and deploy it to the cloud. The page should include: personal introduction, skills, project experience, and contact info — please use placeholders for all personal information. The style should be clean and minimal, responsive for mobile and desktop. Please deploy using Alibaba Cloud ECS."
      },
      {
        label: "Deploy an API service to the cloud",
        value: "/mission Help me quickly deploy an API service to the cloud. I want it to provide /health and /hello endpoints by default, and give me a callable URL with example requests. Keep the configuration as simple and clean as possible."
      }
    ]
  };
  function Te() {
    const T = localStorage.getItem("language") || "";
    return T ? T.split("-")[0] : (navigator.language || "").split("-")[0] || "en";
  }
  if (Y.getGreeting = () => G[Te()] || G.en, Y.getDescription = () => M[Te()] || M.en, Y.getPrompts = () => $[Te()] || $.en, Y.getConfig = function(T) {
    var ve;
    const Z = X(T);
    return {
      ...Z,
      theme: {
        ...Z.theme,
        leftHeader: {
          ...(ve = Z.theme) == null ? void 0 : ve.leftHeader,
          title: "Work with CloudPaw"
        }
      },
      welcome: {
        ...Z.welcome,
        avatar: U
      }
    };
  }, !document.getElementById("cloudpaw-welcome-style")) {
    const T = document.createElement("style");
    T.id = "cloudpaw-welcome-style", T.textContent = `
      [class*="chat-anywhere-welcome-default"] [class*="description"],
      [class*="message-list-welcome"] [class*="description"] {
        white-space: pre-line !important;
        text-align: center !important;
      }
    `, document.head.appendChild(T);
  }
  console.info("[cloudpaw] Patched welcome config & theme via configProvider");
}
Ft();
